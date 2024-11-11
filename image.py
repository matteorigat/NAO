# Python 3.12 - Gemini Server
import os
import base64
from io import BytesIO
import cv2
import google.generativeai as genai
import numpy as np
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configura l'API key di Gemini
genai.configure(api_key="AIzaSyADK9s_80_2xbCa3_CH1_fZvIuWvxOg468")

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-pro-002",
  generation_config=generation_config,
  system_instruction="sei il robot nao. rispondi sempre in prima persona. massimo 3 righe",
)


def analyze_image(image_path):
    try:
        # Carica il file immagine su Gemini
        file = genai.upload_file(image_path, mime_type="image/jpeg")
        print(f"File '{file.display_name}' caricato con successo: {file.uri}")

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

@app.route('/request_analysis', methods=['GET'])
def request_analysis():
    try:
        # Richiedi l'immagine dal server NAO
        nao_response = requests.get("http://localhost:6666/capture_image")

        if nao_response.status_code != 200:
            return jsonify({"error": "Impossibile acquisire l'immagine dal robot NAO"}), 500

        image_base64 = nao_response.json().get("image")
        image_data = base64.b64decode(image_base64)

        if not image_data:
            return jsonify({"error": "Immagine vuota ricevuta dal server NAO"}), 400


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
            return jsonify({"error": "Impossibile ottenere una descrizione dell'immagine"}), 400

        #Invia la descrizione da pronunciare al server NAO
        nao_say_response = requests.post("http://localhost:6666/say", json={"message": description})

        if nao_say_response.status_code == 200:
            return jsonify({"description": description}), 200
        else:
            return jsonify({"error": "Impossibile far pronunciare il messaggio al robot NAO"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500




if __name__ == '__main__':
    app.run(host="127.0.0.1", port=6667)