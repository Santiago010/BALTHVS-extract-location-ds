import json
import os

def decode_text(text):
    """Intenta decodificar usando Latin-1 → UTF-8"""
    try:
        return bytes(text, "latin1").decode("utf-8")
    except UnicodeDecodeError:
        return text  # Si hay error, devolver el texto original

def process_json(file_path):
    """Carga, decodifica y filtra los datos del JSON"""
    try:
        # Leer el JSON
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Obtener el nombre del primer participante
        participant_name = decode_text(data["participants"][0]["name"]) if "participants" in data and data["participants"] else "Desconocido"

        # Filtrar y decodificar mensajes
        messages = []
        if "messages" in data:
            for message in data["messages"]:
                filtered_message = {
                    "sender_name": decode_text(message["sender_name"]),
                    "content": decode_text(message["content"]) if "content" in message else ""
                }
                messages.append(filtered_message)

        # Si no hay mensajes relevantes, no agregar el objeto
        if messages:
            return {
                "messages": messages,
                "participant_name": participant_name  # Guardar el nombre del primer participante
            }
        else:
            return None  # No agregar objetos vacíos

    except Exception as e:
        print(f"❌ Error procesando {file_path}: {e}")
        return None  # Retorna None si hay un error

def process_inbox(inbox_path):
    """Recorre todas las carpetas en 'inbox' y procesa cada 'message_1.json' encontrado"""
    all_messages = []  # Lista para almacenar todos los mensajes
    total_processed = 0

    # Recorrer todas las carpetas dentro de "inbox"
    for folder_name in os.listdir(inbox_path):
        folder_path = os.path.join(inbox_path, folder_name)
        json_file = os.path.join(folder_path, "message_1.json")

        # Verificar si es una carpeta y contiene el archivo message_1.json
        if os.path.isdir(folder_path) and os.path.isfile(json_file):
            decoded_data = process_json(json_file)
            if decoded_data:
                all_messages.append(decoded_data)  # Agregar al array
                print(f"✅ Procesado: {json_file} | Participante: {decoded_data['participant_name']}")
                total_processed += 1  # Contar archivos procesados

    # Eliminar objetos vacíos en caso de que haya quedado alguno
    all_messages = [msg for msg in all_messages if msg.get("messages")]

    # Guardar todos los mensajes en un solo archivo JSON
    output_file = os.path.join(inbox_path, "all_messages_decode.json")
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump({"all_message": all_messages}, file, indent=4, ensure_ascii=False)

    print(f"\n🚀 Proceso completado. Archivos decodificados: {total_processed}")
    print(f"✅ Todos los mensajes guardados en: {output_file}")

# Ruta a la carpeta 'inbox' (ajústala si es necesario)
inbox_directory = "."

# Verificar si la carpeta existe antes de procesar
if os.path.exists(inbox_directory) and os.path.isdir(inbox_directory):
    process_inbox(inbox_directory)
else:
    print("❌ Error: La carpeta 'inbox' no existe o no es válida.")