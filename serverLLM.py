# Python 3.12 - Gemini Server
import os
import base64
import re
from io import BytesIO
import cv2
import google.generativeai as genai
import numpy as np
from flask import Flask, request, jsonify
import requests


# Configura l'API key di Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash-exp-0827",
  generation_config=generation_config,
  system_instruction="sei il robot nao. rispondi sempre in prima persona come farebbe una persona. dai risposte concise, lunghe solo se servono.",
)

chat = model.start_chat()

def upload_to_gemini(path, mime_type=None):
  """Uploads the given file to Gemini.

  See https://ai.google.dev/gemini-api/docs/prompting_with_media
  """
  file = genai.upload_file(path, mime_type=mime_type)
  print(f"Uploaded file '{file.display_name}' as: {file.uri}")
  return file


def analyze_audio(audio_path):
    try:
        # Carica il file audio su Gemini
        file = upload_to_gemini(audio_path, mime_type="audio/ogg")

        # Invia un messaggio al modello per ottenere una risposta dall'audio
        response = chat.send_message([file, "rispondi a questa domanda"]) #stream=True
        # for chunk in response:
        #     print(chunk.text)
        #     print("_" * 80)
        # Restituisce la risposta del modello
        return response.text

    except Exception as e:
        return "Impossibile ottenere una descrizione dell'audio. " + str(e)


def analyze_image(image_path):
    try:
        # Carica il file immagine su Gemini
        file = upload_to_gemini(image_path, mime_type="image/jpeg")

        # Avvia una sessione di chat con il modello
        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        file,
                        "",
                    ],
                },
            ]
        )

        # Invia un messaggio al modello per ottenere la descrizione dell'immagine
        response = chat_session.send_message("Cosa vedi nell'immagine?")
        # Restituisce la descrizione dell'immagine
        return response.text

    except Exception as e:
        # Gestione degli errori
        print(f"Errore durante l'analisi dell'immagine: {e}")
        return "Impossibile ottenere una descrizione dell'immagine."





############   CHIAMATE A NAO   ############




def clean_message(message):
    # Rimuovi caratteri speciali non supportati
    return re.sub(r'[^a-zA-Z0-9\s,.!?]', '', message)

# Funzione per inviare il messaggio generato al server Flask
def say(message):
    #message = str(message).strip()
    #message = clean_message(message)

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


def request_photo():
    try:
        # Richiedi l'immagine dal server NAO
        nao_response = requests.get("http://localhost:6666/capture_image")

        if nao_response.status_code != 200:
            print("Impossibile acquisire l'immagine dal robot NAO")

        image_base64 = nao_response.json().get("image")
        image_data = base64.b64decode(image_base64)

        if not image_data:
            print("Immagine vuota ricevuta dal server NAO.")


        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Immagine non valida, impossibile decodificare.")

        # Salva l'immagine come file .jpg
        image_path = './tmp/image.jpg'
        cv2.imwrite(image_path, image)

        # Analizza l'immagine
        description = analyze_image(image_path)

        if description is None:
            print("Impossibile ottenere una descrizione dell'immagine.")

        #Invia la descrizione da pronunciare al server NAO
        nao_say_response = requests.post("http://localhost:6666/say", json={"message": description})

        if nao_say_response.status_code == 200:
            print("Messaggio inviato con successo al robot NAO!", description)
        else:
            print("Impossibile far pronunciare il messaggio al robot NAO")

    except Exception as e:
        print(f"Errore durante l'analisi dell'immagine: {e}")


def request_audio():

    # Fai la richiesta GET per ottenere l'audio
    response = requests.get("http://127.0.0.1:6666/record_audio")

    if response.status_code == 200:
        # Estrai la stringa base64 dalla risposta JSON
        data = response.json()
        audio_base64 = data.get("audio")

        if audio_base64:
            # Decodifica la stringa base64 in dati binari
            audio_data = base64.b64decode(audio_base64)

            # Scrivi i dati audio in un file .ogg
            with open("./tmp/received_audio.ogg", "wb") as audio_file:
                audio_file.write(audio_data)

            return "File audio ricevuto e salvato come 'received_audio.ogg'."
        else:
            return "Errore: Non è stato trovato l'audio nella risposta."
    else:
        return f"Errore nella richiesta: {response.status_code}"