import os
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuración de la API
OLLAMA_API_URL = "http://localhost:11434/api/generate"
DEEPSEEK_MODEL = "deepseek-r1"
MAX_WORKERS = 5  # Número de hilos en paralelo

def ask_deepseek(conversation_text, participant_name):
    """ Envía la conversación a DeepSeek para extraer ubicación y contexto """

    prompt = f"""
    Analyze the following text and extract any location mentioned, it may be a city, a country, or a state in the United States, etc.
    Return the response as a JSON object with the following format:

    {{
        "participant": "{participant_name}",
        "location": "<EXTRACTED LOCATION>",
        "summary": "<CONVERSATION SUMMARY>"
    }}

    If the text does not mention a location, return `"location": "No location specified"`.

    Text:
    {conversation_text}
    """

    payload = {
        "model": DEEPSEEK_MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        print(f"📤 Sending request for: {participant_name}")  # Indicar que se está enviando la solicitud
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=15)  # Establecer un límite de espera
        response.raise_for_status()

        # Obtener y mostrar la respuesta en consola
        deepseek_response = response.json().get("response", "No location specified")
        print(json.dumps(deepseek_response, indent=4))  # Mostrar el JSON de respuesta bien formateado
        
        return deepseek_response

    except requests.exceptions.Timeout:
        return {"participant": participant_name, "location": "Error: Timeout", "summary": ""}

    except requests.exceptions.RequestException as e:
        return {"participant": participant_name, "location": "Error retrieving location", "summary": ""}

def process_conversation(participant):
    """Extrae mensajes de la otra persona y envía a DeepSeek"""
    
    # Obtener el nombre del participante
    participant_name = participant.get("participant_name", "Unknown")

    # Filtrar los mensajes que NO son de 'balthvsmusic'
    messages = participant.get("messages", [])
    conversation_text = " ".join(
        msg["content"] for msg in messages if msg.get("content") and msg["sender_name"] != "balthvsmusic"
    )
    
    # Llamar a DeepSeek con la conversación filtrada
    respuesta = ask_deepseek(conversation_text,participant_name)

    print({"participant": participant_name, "respuesta DeepSeek": respuesta})

# Función para procesar el JSON completo en paralelo
def process_json(file_path):
    """ Procesa el JSON en paralelo usando múltiples hilos """
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if "all_message" not in data:
        print("❌ Error: JSON structure incorrect.")
        return []

    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_participant = {executor.submit(process_conversation, p): p for p in data["all_message"]}

        for future in as_completed(future_to_participant):
            results.append(future.result())

    return results

# Función principal
def main():
    input_file = "couple_messages.json"
    output_folder = "resultados"

    os.makedirs(output_folder, exist_ok=True)

    print(f"🚀 Starting processing: {input_file}")
    results = process_json(input_file)

    output_file = os.path.join(output_folder, "optimized_results.json")
    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(results, outfile, indent=4, ensure_ascii=False)

    print(f"✅ Results saved in: {output_file}")

if __name__ == "__main__":
    main()