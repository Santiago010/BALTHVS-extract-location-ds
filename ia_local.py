import requests

# Configuración de la API
OLLAMA_API_URL = "http://localhost:11434/api/generate"  # URL de la API de Ollama/DeepSeek
DEEPSEEK_MODEL = "deepseek-r1"  # Nombre del modelo que estás usando

# Función para enviar un prompt a DeepSeek R1
def ask_deepseek(prompt):
    payload = {
        "model": DEEPSEEK_MODEL,
        "prompt": prompt,
        "stream": False  # Para recibir la respuesta completa de una vez
    }
    
    try:
        # Enviar la solicitud a la API
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()  # Lanza un error si la solicitud falla
        
        # Devolver la respuesta generada por DeepSeek
        return response.json()["response"].strip()
    except Exception as e:
        print(f"Error al contactar a DeepSeek: {e}")
        return "Error"

# Ejemplo de uso
if __name__ == "__main__":
    prompt = "Hola, ¿cómo estás?"
    respuesta = ask_deepseek(prompt)
    print(f"Respuesta de DeepSeek: {respuesta}")