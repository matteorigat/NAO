import os
import base64
import time
import re
import cv2
import numpy as np
import requests
import threading
from flask import Flask, request, jsonify
from naoqi import ALProxy, ALModule, ALBroker
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

leds = ALProxy("ALLeds", NAO_IP, NAO_PORT)
rotate_event = threading.Event()
tracking_event = threading.Event()


def clean_message(message):
    # Rimuovi caratteri speciali non supportati
    return re.sub(r'[^a-zA-Z0-9\s,.!?]', '', message)

@app.route('/say', methods=['POST'])
def say():

    rotate_event.clear()
    leds.fadeRGB("FaceLeds", 0xffffff, 0.2)

    # Ottiene il messaggio dal corpo della richiesta
    data = request.json
    message = data.get('message')

    # Connessione al modulo ALTextToSpeech
    tts = ALProxy("ALTextToSpeech", NAO_IP, NAO_PORT)
    #animate = ALProxy("ALAnimatedSpeech", NAO_IP, NAO_PORT)
    configuration = {"bodyLanguageMode": "random"}

    if not message:
        return jsonify({"error": "No message provided"}), 400

    try:
        #clean_msg = clean_message(message)
        clean_msg_utf8 = message.encode('utf-8')
        print ("Sending message to NAO: ", clean_msg_utf8)
        # Invia il messaggio al robot NAO per la sintesi vocale
        tts.say("\\style=joyful\\ " + clean_msg_utf8)
        #animate.say(clean_msg_utf8, configuration)
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


# def download_file(file_path_on_nao, local_filename):
#     try:
#         # Crea una connessione SSH con il robot
#         ssh = paramiko.SSHClient()
#         ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#         ssh.connect(NAO_IP, username=NAO_USERNAME, password=NAO_PASSWORD)
#
#         # Usa SFTP per scaricare il file
#         sftp = ssh.open_sftp()
#         sftp.get(file_path_on_nao, "./tmp/" +local_filename)  # Scarica il file con il nome locale
#         sftp.close()
#         ssh.close()
#
#         print("File " + local_filename +" scaricato con successo!")
#
#     except Exception as e:
#         print("Errore durante il download del file: ", e)


# def detect_silence(audio_proxy):
#     audio_proxy.enableEnergyComputation()
#
#     # Soglia di energia per considerare il silenzio
#     silence_threshold = 300  # 300 valore buono
#
#     # Durata minima del silenzio in secondi
#     silence_duration = 1  # Durata del silenzio per considerarlo rilevante
#
#     start_time = time.time()  # Tempo di inizio
#     while True:
#         # Ottieni l'energia dei microfoni
#         front_energy = audio_proxy.getFrontMicEnergy()
#         left_energy = audio_proxy.getLeftMicEnergy()
#         right_energy = audio_proxy.getRightMicEnergy()
#         rear_energy = audio_proxy.getRearMicEnergy()
#
#         # Calcola l'energia media dei microfoni
#         average_energy = (front_energy + left_energy + right_energy + rear_energy) / 4.0
#
#         if average_energy < silence_threshold:
#             if time.time() - start_time > silence_duration:
#                 print("Silenzio rilevato!")
#                 break  # Rilevato il silenzio, esci dal ciclo
#         else:
#             start_time = time.time()  # Reset del timer se viene rilevato un suono
#
#         time.sleep(0.1)  # Pausa per evitare sovraccarico CPU

# @app.route('/record_audio', methods=['GET'])
# def record_audio():
#     try:
#         leds.fadeRGB("FaceLeds", 0x42ff42, 0.5)
#
#         audio_proxy = ALProxy("ALAudioDevice", NAO_IP, NAO_PORT)
#
#         filename_audio = "audio_LLM" + ".ogg" #datetime.now().strftime("%Y%m%d_%H%M%S")
#         file_path_on_nao = "/home/nao/recordings/" + filename_audio
#
#         audio_proxy.stopMicrophonesRecording()
#         silence_duration = 2
#         start_time , stop_time = 0, 0
#
#         while (stop_time - start_time) < silence_duration:
#             start_time = time.time()
#             audio_proxy.startMicrophonesRecording(file_path_on_nao)
#             detect_silence(audio_proxy)
#             audio_proxy.stopMicrophonesRecording()
#             stop_time = time.time()
#
#         print("Registrazione completata.")
#         leds.off("FaceLeds")
#         rotate_event.set()
#         rotate_thread = threading.Thread(target=rotate_eyes)
#         rotate_thread.start()
#
#         audio_proxy.stopMicrophonesRecording()
#
#         # Crea una connessione SSH e SFTP per leggere il file senza scaricarlo fisicamente
#         ssh = paramiko.SSHClient()
#         ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#         ssh.connect(NAO_IP, username=NAO_USERNAME, password=NAO_PASSWORD)
#
#         # Usa SFTP per ottenere il file come oggetto binario in memoria
#         sftp = ssh.open_sftp()
#         with sftp.open(file_path_on_nao, 'rb') as audio_file:
#             audio_data = audio_file.read()
#
#         # Codifica i dati audio in base64
#         audio_base64 = base64.b64encode(audio_data).decode('utf-8')
#
#         # Chiudi la connessione SFTP
#         sftp.close()
#         ssh.close()
#
#         # Restituisci il file audio come base64 in formato JSON
#         return jsonify({"audio": audio_base64})
#
#
#     except Exception as e:
#
#         print("Errore durante la registrazione: ", e)
#         return jsonify({"error": str(e)}), 500

class AudioCaptureModule(ALModule):  # NAOqi module for capturing audio
    """
    This is a custom module built on top of NAOqi framework for managing audio capture from NAO's microphones.
    It extends ALModule class from the NAOqi framework and defines methods to to start and stop audio capture, process audio data, and retrieve audio chunks.
    """

    def __init__(self, name):
        ALModule.__init__(self, name)
        self.audio_device = ALProxy("ALAudioDevice", NAO_IP, NAO_PORT)
        self.is_listening = False
        self.buffers = []

    def start_listening(self):
        self.audio_device.setClientPreferences(self.getName(), 16000, 3,
                                               0)  # sample rate of 16000 Hz, channelparam 3 (front channel), and a deinterleaving flag of 0 (only relevant for channelparam 0 (all channels))
        self.audio_device.subscribe(self.getName())
        self.is_listening = True

    def stop_listening(self):
        self.audio_device.unsubscribe(self.getName())
        self.is_listening = False

    def processRemote(self, nbOfChannels, nbOfSamplesByChannel, timeStamp,
                      inputBuffer):  # callback method that is triggered whenever new audio data is available
        # print("received audio data from NAO with the following parameters: nbOfChannels = " + str(
        #     nbOfChannels) + ", nbOfSamplesByChannel = " + str(nbOfSamplesByChannel) + ", timeStamp = " + str(
        #     timeStamp[0]) + " sec " + str(timeStamp[1]) + " musec" + ", length of inputBuffer = " + str(
        #     len(inputBuffer)))
        if self.is_listening:
            self.buffers.append(inputBuffer)

    def get_audio_chunk(self):
        if self.buffers:
            return self.buffers.pop(0)  # return the oldest audio chunk
        else:
            print("no audio data available")
            return None

try:
    pythonBroker = ALBroker("pythonBroker", "0.0.0.0", 0, NAO_IP, NAO_PORT)  # broker connection: essential for communicating between the module and the NAOqi runtime
    global AudioCapture
    AudioCapture = AudioCaptureModule("AudioCapture")  # create an instance of the AudioCaptureModule class
    print("AudioCapture module initialized")
except RuntimeError:
    print("Error initializing broker!")
    exit(1)

@app.route("/start_listening", methods=["POST"])
def start_listening():
    # print("Received a request to start listening, current length of server buffer:", len(AudioCapture.buffers))
    AudioCapture.start_listening()
    return jsonify(success=True)


@app.route("/stop_listening", methods=["POST"])
def stop_listening():
    # print("Received a request to stop listening, current length of server buffer:", len(AudioCapture.buffers))
    AudioCapture.stop_listening()
    return jsonify(success=True)


@app.route("/get_audio_chunk", methods=["GET"])
def get_audio_chunk():
    sleep_time = 0.01

    # print("Received a request to get an audio chunk, current length of server buffer:", len(AudioCapture.buffers))
    audio_data = AudioCapture.get_audio_chunk()
    if audio_data is not None:
        return audio_data  # send the audio data as a response
    else:
        print("Server buffer is empty, waiting for audio data...")
        while audio_data is None:  # wait until audio data is available
            audio_data = AudioCapture.get_audio_chunk()
            time.sleep(sleep_time)
        return audio_data


@app.route("/get_server_buffer_length", methods=["GET"])
def get_server_buffer_length():
    # print("Received a request to print the length of the server buffer, current length of server buffer:",
    #       len(AudioCapture.buffers))
    return jsonify(length=len(AudioCapture.buffers))

def rotate_eyes():
    leds = ALProxy("ALLeds", NAO_IP, NAO_PORT)
    #leds.fadeRGB("FaceLeds", 0x0fff0f, 0.2)

    # Lista dei LED in ordine per simulare il movimento circolare
    led_pairs = [
        ["Face/Led/Blue/Right/0Deg/Actuator/Value", "Face/Led/Blue/Left/45Deg/Actuator/Value"],
        ["Face/Led/Blue/Right/45Deg/Actuator/Value", "Face/Led/Blue/Left/90Deg/Actuator/Value"],
        ["Face/Led/Blue/Right/90Deg/Actuator/Value", "Face/Led/Blue/Left/135Deg/Actuator/Value"],
        ["Face/Led/Blue/Right/135Deg/Actuator/Value", "Face/Led/Blue/Left/180Deg/Actuator/Value"],
        ["Face/Led/Blue/Right/180Deg/Actuator/Value", "Face/Led/Blue/Left/225Deg/Actuator/Value"],
        ["Face/Led/Blue/Right/225Deg/Actuator/Value", "Face/Led/Blue/Left/270Deg/Actuator/Value"],
        ["Face/Led/Blue/Right/270Deg/Actuator/Value", "Face/Led/Blue/Left/315Deg/Actuator/Value"],
        ["Face/Led/Blue/Right/315Deg/Actuator/Value", "Face/Led/Blue/Left/0Deg/Actuator/Value"]
    ]

    # Durata del singolo passo dell'animazione
    led_on_duration = 0.1

    active_leds = []
    leds.off("FaceLeds")
    firstRun = True

    while rotate_event.is_set():
        for i in range(len(led_pairs)):
            if len(active_leds) > 1:
                leds.createGroup("previousLeds", active_leds)
                leds.setIntensity("previousLeds", 0.5)
                active_leds = []

            leds.createGroup("activeLeds", led_pairs[i])
            leds.setIntensity("activeLeds", 1.0)

            active_leds.append(led_pairs[i][0])
            active_leds.append(led_pairs[i][1])

            time.sleep(led_on_duration)

            if(firstRun):
                firstRun = False
            else:
                leds.setIntensity("previousLeds", 0.0)

            if not rotate_event.is_set():
                break


# def trackFace():
# 
#     # Create a proxy to ALFaceDetection
#     motionProxy = ALProxy("ALMotion", NAO_IP, NAO_PORT)
#     postureProxy = ALProxy("ALRobotPosture", NAO_IP, NAO_PORT)
#     trackerProxy = ALProxy("ALTracker", NAO_IP, NAO_PORT)
# 
#     #motionProxy.wakeUp()
#     motionProxy.setStiffnesses("Body", 1.0)
# 
#     print ("Starting tracker")
# 
#     # Add target to track.
#     mode = "Head"
#     targetName = "Face"
#     faceWidth = 0.6
#     trackerProxy.registerTarget(targetName, faceWidth)
# 
#     trackerProxy.track(targetName)
# 
#     try:
#         while tracking_event.is_set():
#             time.sleep(1)
#     except KeyboardInterrupt:
#         print ("Interrupted by user, stopping tracker")
#     finally:
#         leds.fadeRGB("FaceLeds", 0xffffff, 0.5)
#         trackerProxy.stopTracker()
#         trackerProxy.unregisterAllTargets()
#         motionProxy.rest()



if __name__ == '__main__':
    #tracking_event.set()
    #track_thread = threading.Thread(target=trackFace)
    #track_thread.start()

    try:
        # Avvia il server Flask in un thread separato
        server_thread = threading.Thread(target=lambda: app.run(host='127.0.0.1', port=6666))
        server_thread.daemon = True
        server_thread.start()

        print("Premi INVIO per terminare il programma.")
        raw_input()  # Attendi che l'utente prema INVIO

    finally:
        # Interrompi eventi e thread
        print("Chiusura in corso...")
        #tracking_event.clear()
        rotate_event.clear()
        print("Programma terminato.")



