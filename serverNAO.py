import os
import base64
import time
import re
import cv2
import numpy as np
import requests
from flask import Flask, request, jsonify
from naoqi import ALProxy
import paramiko
from datetime import datetime

from tornado.autoreload import start

# Configurazione del server Flask
app = Flask(__name__)

# Configurazione della connessione con il robot NAO
#NAO_IP = "127.0.0.1"
NAO_IP = "192.168.1.166"
NAO_PORT = 9559

NAO_USERNAME = "nao"
NAO_PASSWORD = "2468"


def clean_message(message):
    # Rimuovi caratteri speciali non supportati
    return re.sub(r'[^a-zA-Z0-9\s,.!?]', '', message)

@app.route('/say', methods=['POST'])
def say():
    # Ottiene il messaggio dal corpo della richiesta
    data = request.json
    message = data.get('message')

    # Connessione al modulo ALTextToSpeech
    tts = ALProxy("ALTextToSpeech", NAO_IP, NAO_PORT)

    if not message:
        return jsonify({"error": "No message provided"}), 400

    try:
        #clean_msg = clean_message(message)
        clean_msg_utf8 = message.encode('utf-8')
        print ("Sending message to NAO: ", clean_msg_utf8)
        # Invia il messaggio al robot NAO per la sintesi vocale
        tts.say(clean_msg_utf8)
        return jsonify({"status": "Message sent to NAO"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/capture_image', methods=['GET'])
def capture_image():
    video_device = ALProxy("ALVideoDevice", NAO_IP, NAO_PORT)

    AL_kTopCamera = 0
    AL_kQVGA = 2  # 1: 320x240  2: 640x480
    AL_kBGRColorSpace = 13

    capture_device = video_device.subscribeCamera("test", AL_kTopCamera, AL_kQVGA, AL_kBGRColorSpace, 10)

    # get image
    result = video_device.getImageRemote(capture_device)
    video_device.unsubscribe(capture_device)

    if result == None:
        return jsonify({"error": "Cannot capture."}), 500
    elif result[6] == None:
        return jsonify({"error": "No image data string."}), 500

    try:
        width = result[0]
        height = result[1]
        array = result[6]
        print("Image size: ", width, height)

        # Convert to OpenCV image
        openCV_image = np.ndarray((height, width, 3), dtype=np.uint8, buffer=array)

        # Optionally, show the image (for debugging)
        #cv2.imshow("capture", openCV_image)
        #cv2.waitKey(1)  # Prevent the window from freezing

        # Convert to base64
        _, buffer = cv2.imencode('.jpg', openCV_image)  # Convert image to .jpg format
        image_base64 = base64.b64encode(buffer).decode('utf-8')

        print("Image sent to client:", image_base64[:50])  # Print first 50 chars of the base64 string
        return jsonify({"image": image_base64}), 200

    except Exception as e:
        return jsonify({"error": "Failed to process image: {}".format(str(e))}), 500


def download_file(file_path_on_nao, local_filename):
    try:
        # Crea una connessione SSH con il robot
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(NAO_IP, username=NAO_USERNAME, password=NAO_PASSWORD)

        # Usa SFTP per scaricare il file
        sftp = ssh.open_sftp()
        sftp.get(file_path_on_nao, "./tmp/" +local_filename)  # Scarica il file con il nome locale
        sftp.close()
        ssh.close()

        print("File " + local_filename +" scaricato con successo!")

    except Exception as e:
        print("Errore durante il download del file: ", e)


def detect_silence(audio_proxy):
    audio_proxy.enableEnergyComputation()

    # Soglia di energia per considerare il silenzio
    silence_threshold = 300  # 300 valore buono

    # Durata minima del silenzio in secondi
    silence_duration = 1  # Durata del silenzio per considerarlo rilevante

    start_time = time.time()  # Tempo di inizio
    while True:
        # Ottieni l'energia dei microfoni
        front_energy = audio_proxy.getFrontMicEnergy()
        left_energy = audio_proxy.getLeftMicEnergy()
        right_energy = audio_proxy.getRightMicEnergy()
        rear_energy = audio_proxy.getRearMicEnergy()

        # Calcola l'energia media dei microfoni
        average_energy = (front_energy + left_energy + right_energy + rear_energy) / 4.0

        if average_energy < silence_threshold:
            if time.time() - start_time > silence_duration:
                print("Silenzio rilevato!")
                break  # Rilevato il silenzio, esci dal ciclo
        else:
            start_time = time.time()  # Reset del timer se viene rilevato un suono

        time.sleep(0.1)  # Pausa per evitare sovraccarico CPU

@app.route('/record_audio', methods=['GET'])
def record_audio():
    try:
        leds = ALProxy("ALLeds", NAO_IP, NAO_PORT)
        leds.fadeRGB("FaceLeds", 0x0fff0f, 0.2)

        audio_proxy = ALProxy("ALAudioDevice", NAO_IP, NAO_PORT)

        filename_audio = "audio_LLM" + ".ogg" #datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path_on_nao = "/home/nao/recordings/" + filename_audio

        audio_proxy.stopMicrophonesRecording()
        silence_duration = 2
        start_time , stop_time = 0, 0

        while (stop_time - start_time) < silence_duration:
            start_time = time.time()
            audio_proxy.startMicrophonesRecording(file_path_on_nao)
            detect_silence(audio_proxy)
            audio_proxy.stopMicrophonesRecording()
            stop_time = time.time()

        print("Registrazione completata.")
        leds.fadeRGB("FaceLeds", 0xFFFFFF, 1)
        audio_proxy.stopMicrophonesRecording()

        # Crea una connessione SSH e SFTP per leggere il file senza scaricarlo fisicamente
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(NAO_IP, username=NAO_USERNAME, password=NAO_PASSWORD)

        # Usa SFTP per ottenere il file come oggetto binario in memoria
        sftp = ssh.open_sftp()
        with sftp.open(file_path_on_nao, 'rb') as audio_file:
            audio_data = audio_file.read()

        # Codifica i dati audio in base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')

        # Chiudi la connessione SFTP
        sftp.close()
        ssh.close()

        # Restituisci il file audio come base64 in formato JSON
        return jsonify({"audio": audio_base64})


    except Exception as e:

        print("Errore durante la registrazione: ", e)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=6666)
