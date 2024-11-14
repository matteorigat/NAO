import json
import os
import re
import requests
import google.generativeai as genai

# Configurazione della chiave API per Google Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Configurazione del modello di generazione di testo
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Creazione del modello
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
)

chat = model.start_chat()

# # Avvio della sessione di chat
# chat_session = model.start_chat(
#     history=[
#         # Puoi aggiungere qui eventuali messaggi iniziali
#     ]
# )

def clean_message(message):
    # Rimuovi caratteri speciali non supportati
    return re.sub(r'[^a-zA-Z0-9\s,.!?]', '', message)

# Funzione per inviare il messaggio generato al server Flask
def send_to_nao(message):
    message = str(message).strip()
    message = clean_message(message)

    # URL del server Flask che inoltra i messaggi al robot NAO
    url = 'http://localhost:6666/say'

    # Dati da inviare in formato JSON
    data = {"message": message}

    # Invia il messaggio al server Flask
    response = requests.post(url, json=data)

    # Controlla la risposta del server
    if response.status_code == 200:
        print("Messaggio inviato con successo al robot NAO!")
    else:
        print("Errore nell'invio del messaggio:", response.json())

def save_chat_history_to_file(filename="./tmp/chat_history.txt"):
    with open(filename, "w") as file:
        for message in chat.history:
            file.write(f"{message}")

# Funzione per inviare messaggi alla chat
def send_message_to_gemini(message):
    response = chat.send_message(message)
    save_chat_history_to_file()
    return response.text



#send_to_nao(response.text)


if __name__ == '__main__':
    print("Inizia la chat con Gemini (scrivi 'exit' per terminare):")

    while True:
        user_input = input("Tu: ")
        if user_input.lower() == 'exit':
            print("Chat terminata.")
            break

        response_text = send_message_to_gemini(user_input)
        print(f"Gemini: {response_text}")
