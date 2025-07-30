import whisper

def transcribe_audio(filename, model_size="base"):
    model = whisper.load_model(model_size)
    result = model.transcribe(filename)
    text = result["text"]
    with open("recordings/transcript.txt", "w", encoding="utf-8") as f:
        f.write(text)
    return text
