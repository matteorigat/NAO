# Python 3.12 - Gemini Server
import os
import base64
import re
import subprocess
import tempfile

import cv2
import google.generativeai as genai
import numpy as np
# from flask import Flask, request, jsonify
import requests
import speech_recognition as sr
import time
import noisereduce as nr
import soundfile as sf


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
  system_instruction= "Sei il robot NAO. Rispondi sempre adattandoti allo stato d’animo dell’altra persona. Usa risposte brevi se possibile. parli con un solo interlocutore.",
  safety_settings= [
                {
                    'category': 'HARM_CATEGORY_HATE_SPEECH',
                    'threshold': 'BLOCK_ONLY_HIGH'
                },
                {
                    'category': 'HARM_CATEGORY_DANGEROUS_CONTENT',
                    'threshold': 'BLOCK_ONLY_HIGH'
                },
                {
                    'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT',
                    'threshold': 'BLOCK_ONLY_HIGH'
                },
                {
                    'category': 'HARM_CATEGORY_HARASSMENT',
                    'threshold': 'BLOCK_ONLY_HIGH'
                }
            ],
)
# "sei il robot nao, qual'è lo stato d'animo dell'interlocutore? rispondi in non più di tre righe"

chat = model.start_chat()

def upload_to_gemini(path, mime_type=None):
  """Uploads the given file to Gemini.

  See https://ai.google.dev/gemini-api/docs/prompting_with_media
  """
  file = genai.upload_file(path, mime_type=mime_type)
  print(f"Uploaded file '{file.display_name}' as: {file.uri}")
  return file

def wait_for_files_active(files):
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
          print(".", end="", flush=True)
          time.sleep(10)
          file = genai.get_file(name)
        if file.state.name != "ACTIVE":
          raise Exception(f"File {file.name} failed to process")


def analyze_audio(files):
    try:
        # Carica il file audio su Gemini
        #file = upload_to_gemini(audio_path, mime_type="audio/ogg")
        #wait_for_files_active(files)
        # Invia un messaggio al modello per ottenere una risposta dall'audio
        if isinstance(files, list):
            wait_for_files_active(files)
            response = chat.send_message([*files, "rispondi a questa domanda"])  # stream=True "rispondi a questa domanda"
        else:
            response = chat.send_message([files, "rispondi a questa domanda"])
        # for chunk in response:
        #     print(chunk.text)
        #     print("_" * 80)
        # Restituisce la risposta del modello
        return response.text

    except Exception as e:
        return "Impossibile ottenere una descrizione dell'audio. " + str(e)




############   CHIAMATE A NAO   ############


def clean_message(message):
    message = re.sub(r"[^a-zA-ZàèéìòùÀÈÉÌÒÙ0-9\s,.!?']", ",", message)
    message = re.sub(r",*,+", ", ", message)
    message = re.sub(r"\n", " ", message)
    message = re.sub(r"\s+", " ", message)
    message = message.strip()
    print("Messaggio pulito:", message)
    return message

# Funzione per inviare il messaggio generato al server Flask
def say(message):
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



class NaoStream:

    def __init__(self, audio_generator):
        self.audio_generator = audio_generator

    def read(self, size=-1):  # added size parameter, default -1
        try:
            return next(self.audio_generator)
        except StopIteration:
            return b''


class NaoAudioSource(sr.AudioSource):

    def __init__(self, server_url="http://localhost:6666"):
        self.server_url = server_url
        self.stream = None
        self.is_listening = False
        self.CHUNK = 1365  # number of samples per audio chunk
        self.SAMPLE_RATE = 16000  # 16 kHz
        self.SAMPLE_WIDTH = 2  # each audio sample is 2 bytes

    def __enter__(self):  # this is called when using the "with" statement
        requests.post(f"{self.server_url}/start_listening")
        self.is_listening = True
        self.stream = NaoStream(self.audio_generator())  # wrap the generator
        return self  # return object (self) to be used in the with statement

    def audio_generator(self):  # generator function that continuously fetches audio chunks from the server as long as 'self.is_listening' is True

        sampling_frequency = 16000  # 16 kHz
        number_of_samples_per_chunk = 1365
        time_between_audio_chunks = number_of_samples_per_chunk / sampling_frequency  # in seconds
        #corrected_time_between_audio_chunks = time_between_audio_chunks * 0.8

        while self.is_listening:
            response = requests.get(f"{self.server_url}/get_audio_chunk")
            yield response.content  # yield is used to return a value from a generator function, but unlike return, it doesn't terminate the function -> instead, it suspends the function and saves its state for later resumption
            current_buffer_length = requests.get(f"{self.server_url}/get_server_buffer_length").json()["length"]
            correcting_factor = 1.0 / (1.0 + np.exp(current_buffer_length - np.pi))  # if buffer becomes long, the time between audio chunks is decreased
            corrected_time_between_audio_chunks = time_between_audio_chunks * correcting_factor
            time.sleep(corrected_time_between_audio_chunks)  # wait for the next audio chunk to be available

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.is_listening = False
        requests.post(f"{self.server_url}/stop_listening")

def convert_to_ogg(input_wav, output_ogg):
    try:
        # Usa FFmpeg per convertire WAV in OGG
        subprocess.run(
            ["ffmpeg", "-i", input_wav, "-c:a", "libvorbis", "-qscale:a", "5", output_ogg, "-y"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"Converted {input_wav} to {output_ogg}")
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")

def request_audio():
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 1  # seconds of non-speaking audio before a phrase is considered complete
    recognizer.operation_timeout = 4  # increasing the timeout duration
    audio_data = None
    audio_path_wav = "./tmp/received_audio.wav"
    audio_path = "./tmp/received_audio.ogg"

    while True:
        # record audio only if it hasn't been recorded yet
        if audio_data is None:
            with NaoAudioSource() as source:
                print("Recording...")
                #start_time = time.time()
                audio_data = recognizer.listen(source, phrase_time_limit=10, timeout=None)
                #print(f"Recording took {time.time() - start_time} seconds")

                audio_duration = len(audio_data.frame_data) / source.SAMPLE_RATE
                if audio_duration < 1:
                    print("Audio troppo breve, riprovo...")
                    audio_data = None
                    continue

                #start_time = time.time()
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav_file:
                    temp_wav_file.write(audio_data.get_wav_data())
                    temp_wav_file.close()

                    # noise reduction
                    audio, sampling_rate = sf.read(temp_wav_file.name)
                    reduced_audio = nr.reduce_noise(y=audio, sr=sampling_rate)

                    with open(audio_path_wav, "wb") as f:
                        sf.write(f, reduced_audio, sampling_rate)

                    convert_to_ogg(audio_path_wav, audio_path)

                    # print(f"Processing audio took {time.time() - start_time} seconds")
                    start_time = time.time()
                    file = upload_to_gemini(audio_path, mime_type="audio/ogg")
                    print(f"Uploading audio took {time.time() - start_time} seconds")

                    return file









# def analyze_image(image_path):
#     try:
#         # Carica il file immagine su Gemini
#         file = upload_to_gemini(image_path, mime_type="image/jpeg")
#
#         # Avvia una sessione di chat con il modello
#         chat_session = model.start_chat(
#             history=[
#                 {
#                     "role": "user",
#                     "parts": [
#                         file,
#                         "",
#                     ],
#                 },
#             ]
#         )
#
#         # Invia un messaggio al modello per ottenere la descrizione dell'immagine
#         response = chat_session.send_message("Cosa vedi nell'immagine?")
#         # Restituisce la descrizione dell'immagine
#         return response.text
#
#     except Exception as e:
#         # Gestione degli errori
#         print(f"Errore durante l'analisi dell'immagine: {e}")
#         return "Impossibile ottenere una descrizione dell'immagine."








# def request_photo():
#     try:
#         # Richiedi l'immagine dal server NAO
#         nao_response = requests.get("http://localhost:6666/capture_image")
#
#         if nao_response.status_code != 200:
#             print("Impossibile acquisire l'immagine dal robot NAO")
#
#         image_base64 = nao_response.json().get("image")
#         image_data = base64.b64decode(image_base64)
#
#         if not image_data:
#             print("Immagine vuota ricevuta dal server NAO.")
#
#
#         nparr = np.frombuffer(image_data, np.uint8)
#         image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#
#         if image is None:
#             raise ValueError("Immagine non valida, impossibile decodificare.")
#
#         image_path = './tmp/image.jpg'
#         cv2.imwrite(image_path, image)
#
#         description = analyze_image(image_path)
#
#         if description is None:
#             print("Impossibile ottenere una descrizione dell'immagine.")
#
#         nao_say_response = requests.post("http://localhost:6666/say", json={"message": description})
#
#         if nao_say_response.status_code == 200:
#             print("Messaggio inviato con successo al robot NAO!", description)
#         else:
#             print("Impossibile far pronunciare il messaggio al robot NAO")
#
#     except Exception as e:
#         print(f"Errore durante l'analisi dell'immagine: {e}")

# def request_audio():
# 
#     # Fai la richiesta GET per ottenere l'audio
#     response = requests.get("http://127.0.0.1:6666/record_audio")
# 
#     if response.status_code == 200:
#         # Estrai la stringa base64 dalla risposta JSON
#         data = response.json()
#         audio_base64 = data.get("audio")
# 
#         if audio_base64:
#             # Decodifica la stringa base64 in dati binari
#             audio_data = base64.b64decode(audio_base64)
# 
#             # Scrivi i dati audio in un file .ogg
#             with open("./tmp/received_audio.ogg", "wb") as audio_file:
#                 audio_file.write(audio_data)
# 
#             return "File audio ricevuto e salvato come 'received_audio.ogg'."
#         else:
#             return "Errore: Non è stato trovato l'audio nella risposta."
#     else:
#         return f"Errore nella richiesta: {response.status_code}"