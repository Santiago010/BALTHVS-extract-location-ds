import os
import json
import spacy
from concurrent.futures import ThreadPoolExecutor, as_completed

# Cargar el modelo de spaCy
nlp = spacy.load("en_core_web_md")

# Definir la cantidad de hilos para el procesamiento en paralelo
MAX_WORKERS = 4  # Ajusta este número según el rendimiento que desees

def process_conversation(participant):
    """Extrae mensajes de la otra persona y envía a spaCy para extraer ubicaciones."""
    
    # Obtener el nombre del participante
    participant_name = participant.get("participant_name", "Unknown")

    # Filtrar los mensajes que NO son de 'balthvsmusic'
    messages = participant.get("messages", [])
    conversation_text = " ".join(
        msg["content"] for msg in messages if msg.get("content") and msg["sender_name"] != "balthvsmusic"
    )

    return {
        "participant": participant_name,
        "locations": extract_location_spacy(conversation_text)
    }

def extract_location_spacy(text):
    """Extrae ubicaciones (ciudades, países, estados) del texto usando spaCy"""
    doc = nlp(text)
    locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]  # GPE = Geopolitical Entity (ciudades, países, estados)
    return locations if locations else ["No location specified"]

# Función para procesar el JSON completo en paralelo
def process_json(file_path):
    """Procesa el JSON en paralelo usando múltiples hilos"""
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
    input_file = "all_messages_decode.json"
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