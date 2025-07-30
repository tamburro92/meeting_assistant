import ollama

CONTEXT = """
Sei un assistente che trascrive riunioni aziendali.
Il tuo compito è generare minute di riunioni strutturate.
Evita qualsiasi spiegazione, ragionamento interno o markup.
Concentrati su:
- Punti chiave discussi
- Decisioni prese
- Azioni future o task assegnati
"""
def summarize_text(text: str, model_name: str = "mistral", context: str = CONTEXT) -> str:
    if not context:
        context = CONTEXT
    
    response = ollama.generate(
        model=model_name,
        system=context,
        prompt= text,
        think=False,
    )

    return response['response'].strip()

