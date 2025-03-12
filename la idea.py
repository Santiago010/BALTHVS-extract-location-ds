import os
import json
import requests

# Configuración de Ollama/DeepSeek
OLLAMA_API_URL = "http://localhost:11434/api/generate"  # URL de la API de Ollama
DEEPSEEK_MODEL = "deepseek-r1"  # Nombre del modelo que estás usandoº

# Función para enviar una conversación a DeepSeek R1
def ask_deepseek(conversation):
    prompt = f"Analiza la siguiente conversación y extrae la ubicación (ciudad, país o estado) de la persona con la que se está hablando. Si no se menciona una ubicación, devuelve 'No especificado'. Aquí está la conversación: {conversation}"
    
    payload = {
        "model": DEEPSEEK_MODEL,
        "prompt": prompt,
        "stream": False  # Para recibir la respuesta completa de una vez
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()  # Lanza un error si la solicitud falla
        return response.json()["response"].strip()
    except Exception as e:
        print(f"Error al contactar a DeepSeek: {e}")
        return "Error"

# Función para procesar un archivo JSON
def process_json(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    
    results = []
    for message in data:
        if "message" in message:  # Asegúrate de que el mensaje tenga contenido
            location = ask_deepseek(message["message"])
            results.append({
                "user": message.get("sender", "Desconocido"),
                "location": location,
                "conversation_id": message.get("id", "Sin ID")
            })
    
    return results

# Función principal
def main():
    input_folder = "conversaciones"  # Carpeta con los archivos JSON
    output_folder = "resultados"     # Carpeta para guardar los resultados
    
    # Crear la carpeta de resultados si no existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Procesar cada archivo JSON en la carpeta de conversaciones
    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            file_path = os.path.join(input_folder, filename)
            print(f"Procesando: {filename}")
            
            results = process_json(file_path)
            
            # Guardar los resultados en un archivo JSON
            output_file = os.path.join(output_folder, f"resultados_{filename}")
            with open(output_file, "w") as outfile:
                json.dump(results, outfile, indent=4)
            
            print(f"Resultados guardados en: {output_file}")

if __name__ == "__main__":
    main()