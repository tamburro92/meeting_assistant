import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
import os
from recorder import start_recording, stop_recording, use_existing_audio
from transcriber import transcribe_audio
from summarizer import summarize_text
import ollama

class MeetingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Meeting Assistant")
        self.root.geometry("1300x700")

        self.recording_stream = None
        self.recording_state = None  # None, 'recording', 'paused'
        self.current_audio_file = None

        style = ttk.Style()
        style.theme_use("aqua")

        # --- Layout ---
        left_frame = ttk.Frame(root, width=300)
        left_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

        right_frame = ttk.Frame(root)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        # Assegna più spazio alla colonna destra
        root.grid_columnconfigure(0, weight=0)  # left frame fisso, niente espansione
        root.grid_columnconfigure(1, weight=1)  # right frame si espande
        root.grid_rowconfigure(0, weight=1)
        
        # --- Bottoni ---
        self.upload_btn = ttk.Button(left_frame, text="📂 Carica File Audio/Video", command=self.load_audio_file)
        self.upload_btn.pack(pady=5, fill='x')

        self.record_btn = ttk.Button(left_frame, text="🎙️ Inizia Registrazione", command=self.toggle_recording)
        self.record_btn.pack(pady=5, fill='x')

        self.stop_btn = ttk.Button(left_frame, text="🛑 Ferma Registrazione", command=self.stop_recording_full)
        self.stop_btn.pack(pady=5, fill='x')

        # --- Contesto ---
        ttk.Label(left_frame, text="🧠 Contesto (opzionale):").pack(anchor="w", pady=(10, 0))
        self.context_entry = tk.Text(left_frame, height=4, wrap=tk.WORD)
        self.context_entry.pack(fill='x', pady=5)

        # --- Modelli ---
        ttk.Label(left_frame, text="🎧 Modello Whisper:").pack(anchor="w", pady=(10, 0))
        self.whisper_var = tk.StringVar(value="base")
        whisper_options = ["tiny", "base", "small", "medium", "large"]
        self.whisper_dropdown = ttk.Combobox(left_frame, textvariable=self.whisper_var, values=whisper_options, state="readonly")
        self.whisper_dropdown.pack(fill='x')

        ttk.Label(left_frame, text="💬 Modello Riassunto:").pack(anchor="w", pady=(10, 0))
        self.model_var = tk.StringVar()
        self.model_dropdown = ttk.Combobox(left_frame, textvariable=self.model_var, state="readonly")
        self.model_dropdown.pack(fill='x')
        self.load_ollama_models()

        # --- Bottoni azione ---
        self.process_btn = ttk.Button(left_frame, text="⚙️ Processa", command=self.run_processing)
        self.process_btn.pack(pady=10, fill='x')

        self.clear_btn = ttk.Button(left_frame, text="🧹 Pulisci", command=self.clear_output)
        self.clear_btn.pack(pady=5, fill='x')

        # --- Area trascrizione ---
        self._add_text_output_block(right_frame, "📝 Trascrizione:", is_summary=False)

        # --- Area riassunto ---
        self._add_text_output_block(right_frame, "📄 Riassunto:", is_summary=True)

        # --- Barra di stato ---
        self.status_label = ttk.Label(root, text="", foreground="gray")
        self.status_label.grid(row=1, column=0, columnspan=2, sticky="we", pady=(5, 0))

    def _add_text_output_block(self, parent, label_text, is_summary=False):
        label_frame = ttk.Frame(parent)
        label_frame.pack(anchor="w", fill="x")

        ttk.Label(label_frame, text=label_text).pack(side="left")
        copy_btn = ttk.Button(label_frame, text="📋", width=3,
                              command=lambda: self.copy_to_clipboard(self.summary_box if is_summary else self.transcript_box))
        copy_btn.pack(side="right")

        box = scrolledtext.ScrolledText(parent, height=20, wrap=tk.WORD)
        box.pack(fill='both', expand=True, pady=5)

        if is_summary:
            self.summary_box = box
        else:
            self.transcript_box = box

    def update_status(self, message, error=False):
        self.status_label.config(text=message, foreground="red" if error else "green")

    def toggle_recording(self):
        if self.recording_state is None:
            self.recording_stream = start_recording()
            self.recording_state = "recording"
            self.current_audio_file = None
            self.record_btn.config(text="⏸️ Pausa Registrazione")
            self.update_status("Registrazione avviata.")
        elif self.recording_state == "recording":
            self.recording_state = "paused"
            self.record_btn.config(text="▶️ Riprendi Registrazione")
            self.update_status("Registrazione in pausa.")
        elif self.recording_state == "paused":
            self.recording_state = "recording"
            self.record_btn.config(text="⏸️ Pausa Registrazione")
            self.update_status("Registrazione ripresa.")

    def stop_recording_full(self):
        if self.recording_stream:
            path = stop_recording(self.recording_stream)
            self.recording_stream = None
            self.recording_state = None
            self.record_btn.config(text="🎙️ Inizia Registrazione")
            self.current_audio_file = path
            self.update_status("Registrazione fermata. File pronto per il processamento.")

    def load_audio_file(self):
        filepath = filedialog.askopenfilename(
            title="Seleziona un file audio o video",
            filetypes=[("File audio/video", "*.wav *.mp3 *.mp4 *.aac *.mkv *.flac *.m4a"), ("Tutti i file", "*.*")]
        )
        if filepath:
            try:
                self.current_audio_file = use_existing_audio(filepath)
                self.update_status(f"File caricato: {os.path.basename(filepath)}")
            except Exception as e:
                self.update_status(f"Errore nel caricamento: {e}", error=True)

    def run_processing(self):
        if not self.current_audio_file:
            self.update_status("Nessun file caricato o registrato.", error=True)
            return
        self.update_status("Elaborazione in corso...")
        threading.Thread(target=self.process_transcription_and_summary).start()

    def process_transcription_and_summary(self):
        self.transcript_box.delete('1.0', tk.END)
        self.summary_box.delete('1.0', tk.END)

        whisper_model = self.whisper_var.get()
        context = self.context_entry.get("1.0", tk.END).strip()
        model = self.model_var.get()

        try:
            transcript = transcribe_audio(self.current_audio_file, model_size=whisper_model)
            self.transcript_box.insert(tk.END, transcript)

            summary = summarize_text(transcript, model_name=model, context=context)
            self.summary_box.insert(tk.END, summary)

            self.update_status("Trascrizione e riassunto completati.")
        except Exception as e:
            self.update_status(f"Errore durante l'elaborazione: {e}", error=True)

    def clear_output(self):
        self.transcript_box.delete('1.0', tk.END)
        self.summary_box.delete('1.0', tk.END)
        self.context_entry.delete('1.0', tk.END)
        self.update_status("")

    def copy_to_clipboard(self, text_widget):
        text = text_widget.get("1.0", tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.update_status("Testo copiato negli appunti.")

    def load_ollama_models(self):
        try:
            model_infos = ollama.list().get("models", [])
            models = [model.model.split(":")[0] for model in model_infos]
            if not models:
                raise RuntimeError("Nessun modello trovato.")
            default_model = "mistral" if "mistral" in models else models[0]
            self.model_var.set(default_model)
            self.model_dropdown["values"] = models
        except Exception as e:
            self.model_var.set("Errore")
            self.model_dropdown["values"] = []
            self.update_status(f"Errore nel caricamento modelli: {e}", error=True)

