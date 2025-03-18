import json
import requests

OLLAMA_API_URL = "http://localhost:11434/api/generate"
DEEPSEEK_MODEL = "deepseek-r1"

def ask_deepseek(conversation_text, participant_name):
    """ Envía la conversación a DeepSeek y extrae solo el JSON válido """
    prompt = f"""
    Extract any mentioned location from the following text. The location may be a city, country, or U.S. state.

    Return ONLY a JSON object in the exact format below:

    {{
        "participant": "{participant_name}",
        "location": "<EXTRACTED LOCATION>"
    }}

    If no location is mentioned, return:

    {{
        "participant": "{participant_name}",
        "location": "No location specified"
    }}

    Do NOT include any extra text, explanations, or token lists. Return ONLY the JSON.

    Text:
    "{conversation_text}"
    """

    payload = {"model": DEEPSEEK_MODEL, "prompt": prompt, "stream": False}

    try:
        # ⏳ Timeout ilimitado
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=None)
        response.raise_for_status()
        response_data = response.json()

        # 🔹 Extraer la parte JSON de la respuesta
        response_text = response_data.get("response", "")

        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        cleaned_json = response_text[json_start:json_end]

        return json.loads(cleaned_json)

    except json.JSONDecodeError:
        return {"participant": participant_name, "location": "Parsing error"}
    except requests.exceptions.RequestException as e:
        return {"participant": participant_name, "location": f"DeepSeek error: {e}"}

# 🔹 Ejemplo de uso
conversation_text = "hey yalll! We met in Charleston when you played at my friend’s wedding. I’m currently in Costa Rica. Gonna see if I can make it down!! Let's shoot for Denver!"
participant_name = "Elle"

result = ask_deepseek(conversation_text, participant_name)
print(result)