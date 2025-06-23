# 🎙️ Meeting Assistant

**Meeting Assistant** is a local-first desktop app with a user-friendly GUI to **record**, **transcribe**, and **summarize** meetings using:

- 🗣️ [Whisper](https://github.com/openai/whisper) for transcription (runs locally)
- 🧠 [Ollama](https://github.com/ollama/ollama) for summarization with local LLMs
- 📁 Audio/video file support: `.mp3`, `.wav`, `.mp4`, `.m4a`, `.flac`, and more
- 🔒 Fully offline – **no cloud**, your data stays on your machine

## 🖥 Features

- 🎤 Record meetings with your microphone
- 📂 Load existing audio/video files via file picker or drag & drop
- 🧠 Choose local Whisper & Ollama models from dropdowns
- 📝 Optional context input to guide the summary
- ⏯ One-button control for start/pause/resume/stop recording
- ✍️ Transcription and summary displayed side by side
- 🚫 Automatically removes reasoning artifacts like `<think>` from summaries

## 📦 Installation

### 1. Requirements

- Python **3.10+**
- [Ollama](https://ollama.com) installed and running (`ollama serve`)
- `ffmpeg` installed and available in your system PATH
- Local Whisper model support (`faster-whisper`, `whisper.cpp`, or `openai-whisper` with compatible setup)

### 2. Setup

```bash
git clone https://github.com/your-username/meeting-assistant.git
cd meeting-assistant

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

> If you encounter errors installing `openai-whisper`, consider using `faster-whisper` or `whisper.cpp`.

## 🚀 Usage

Launch the application with:

```bash
python app.py
```

You’ll be able to:

1. 🎙 Record a meeting or upload a file
2. 🎛 Choose transcription and summarization models
3. 🧠 (Optionally) enter a custom context
4. ✅ Generate transcription and bullet-point summary

## 📄 Example Summary Output

- Discussed Q3 marketing roadmap and KPIs
- Agreed on launching the campaign by July 15
- Assigned Maria to lead the email automation initiative
- Next check-in: Tuesday, 10:00 AM

## ⚙️ Configuration

Meeting Assistant dynamically loads:
- Available **Ollama models** (`mistral`, `llama3`, `gemma`, etc.)
- Installed **Whisper variants** (e.g., `base`, `small`, `medium`)

It also uses Ollama's `options` API with `"think": false` to suppress reasoning traces from the output.

## 📌 Notes

- Ensure `ollama serve` is running before launching the app
- Transcription is optimized for short- to medium-length meetings
- You can use drag-and-drop or manual file selection to upload media

## ✅ Roadmap

- [ ] Real audio pause/resume with merging
- [ ] Export to Markdown, PDF, or Notion
- [ ] Language and speaker diarization support

## 🤝 Contributing

Pull requests are welcome! If you encounter bugs or have feature ideas, feel free to open an issue.

## 🛡 License

MIT License – free to use, modify, and distribute.

**Made with ❤️ for efficient, private meeting management.**