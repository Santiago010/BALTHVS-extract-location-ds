import os
import json
import requests

# Configuración de la API
OLLAMA_API_URL = "http://localhost:11434/api/generate"
DEEPSEEK_MODEL = "deepseek-r1"

# Función para enviar un prompt a DeepSeek R1
def ask_deepseek(prompt):
    payload = {
        "model": DEEPSEEK_MODEL,
        "prompt": prompt,
        "stream": False  # Para recibir la respuesta completa de una vez
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()  
        response_data = response.json()
        return response_data.get("response", {})
    except Exception as e:
        print(f"❌ Error al contactar a DeepSeek: {e}")
        return {}

# Función para procesar el archivo JSON
def process_json(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)

    if "all_message" not in data:
        print("❌ Error: El archivo JSON no tiene la estructura esperada.")
        return {}

    results = []

    # Procesamos cada conversación individualmente
    for idx, participant in enumerate(data["all_message"], start=1):
        messages = participant.get("messages", [])
        participant_name = messages[0].get("sender_name", "Desconocido") if messages else "Desconocido"

        # Unimos los mensajes de este participante en una sola conversación
        conversation = "\n".join(
            f"{msg['sender_name']}: {msg['content']}"
            for msg in messages if msg.get("content")
        )

        # Creamos un prompt único para este participante
        prompt = f"""
        You are an AI assistant specialized in analyzing JSON data. Your task is to carefully read the following conversation and perform the following actions:

        1. Identify the participant: {participant_name}.
        2. Extract any mention of a geographic location (city, country, state) in the conversation.
        3. If no location is mentioned, return 'No location specified'.
        4. Provide a concise summary of what was discussed.

        Conversation:
        {conversation}
        """

        print(f"📤 Enviando conversación #{idx} a DeepSeek... ({participant_name})")
        
        response = ask_deepseek(prompt)

        # Guardamos la respuesta junto con el nombre del participante

        print(response)
        results.append({
            "participant": participant_name,
            "response": response
        })

    return results

# Función principal
def main():
    input_file = "couple_messages.json"
    output_folder = "resultados"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    print(f"🚀 Procesando archivo: {input_file}")
    results = process_json(input_file)

    # Guardar los resultados en un archivo JSON
    output_file = os.path.join(output_folder, "resultados_all_messages.json")
    with open(output_file, "w") as outfile:
        json.dump(results, outfile, indent=4, ensure_ascii=False)

    print(f"✅ Resultados guardados en: {output_file}")

if __name__ == "__main__":
    main()