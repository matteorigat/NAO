import re
import time
import threading
import requests
import random
from flask import Flask, request, jsonify
from naoqi import ALProxy, ALModule, ALBroker

from Gestures_new import Happiness1, Happiness2, Happiness3
from Gestures_new import Sadness1, Sadness2, Sadness3
from Gestures_new import Anger1, Anger2, Anger3
from Gestures_new import Fear1, Fear2, Fear3
from Gestures_new import Sadness3reverse, Fear3reverse

# Configurazione del server Flask
app = Flask(__name__)

# Configurazione della connessione con il robot NAO
#NAO_IP = "127.0.0.1"
NAO_IP = "192.168.1.166"
NAO_PORT = 9559

NAO_USERNAME = "nao"
NAO_PASSWORD = "2468"

leds = ALProxy("ALLeds", NAO_IP, NAO_PORT)
tts = ALProxy("ALTextToSpeech", NAO_IP, NAO_PORT)
motionProxy = ALProxy("ALMotion", NAO_IP, NAO_PORT)
postureProxy = ALProxy("ALRobotPosture", NAO_IP, NAO_PORT)
trackerProxy = ALProxy("ALTracker", NAO_IP, NAO_PORT)
memoryProxy = ALProxy("ALMemory", NAO_IP, NAO_PORT)
animate = ALProxy("ALAnimatedSpeech", NAO_IP, NAO_PORT)

rotate_event = threading.Event()
tracking_event = threading.Event()
track_thread = threading.Thread()

GESTURE_MAP = {
    "Anger1": Anger1, "Anger2": Anger2, "Anger3": Anger3,
    "Fear1": Fear1, "Fear2": Fear2, "Fear3": Fear3,
    "Happiness1": Happiness1, "Happiness2": Happiness2, "Happiness3": Happiness3,
    "Sadness1": Sadness1, "Sadness2": Sadness2, "Sadness3": Sadness3,
    "Sadness3reverse": Sadness3reverse, "Fear3reverse": Fear3reverse
}

lastPose = "Stand"

tag_pose_map = {
    "happy": ["Happiness1", "Happiness3"],
    "sad": ["Sadness1", "Sadness3"],
    "angry": ["Anger1", "Anger2"],
    "fear": ["Fear1", "Fear2"],
    "rst": ["Stand"]
}

@app.route('/say', methods=['POST'])
def say():
    global tracking_event, track_thread, lastPose

    rotate_event.clear()
    time.sleep(0.1)
    leds.fadeRGB("FaceLeds", 0xffffff, 0.8)

    data = request.get_json()
    message = data.get('message')

    if not message:
        return jsonify({"error": "No message provided"}), 400

    segments = re.split(r'(\[.*?\])', message)

    try:
        for segment in segments:
            segment = segment.strip()
            if not segment:
                continue

            if segment.startswith("[") and segment.endswith("]"):
                tag = segment[1:-1]
                handle_tag(tag)
            else:
                message_utf8 = segment.encode('utf-8')
                print("Sending message to NAO:", message_utf8)
                tts.say(message_utf8)

        if lastPose != "Stand":
            postureProxy.goToPosture("Stand", 0.4)
            lastPose = "Stand"

        if not tracking_event.is_set():
            tracking_event.set()
            track_thread = threading.Thread(target=trackFace)
            track_thread.start()

        return jsonify({"status": "Message sent to NAO"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def handle_tag(tag):
    """Handle gestures using tag_pose_map."""
    poses = tag_pose_map.get(tag)
    if not poses:
        print("Unknown tag:", tag)
        return

    pose = random.choice(poses) if len(poses) > 1 else poses[0]
    gesture(pose)


def gesture(message):
    global lastPose, tracking_event, track_thread

    if not message or message == lastPose:
        return

    if message == "Stand":
        postureProxy.goToPosture("Stand", 0.4)
        lastPose = "Stand"

        if not tracking_event.is_set():
            tracking_event.set()
            track_thread = threading.Thread(target=trackFace)
            track_thread.start()
        return

    if tracking_event.is_set():
        tracking_event.clear()

    gesture_class = GESTURE_MAP.get(message)
    if gesture_class:
        lastPose = message
        gesture_class.execute_gesture(NAO_IP, NAO_PORT)
    else:
        print("Invalid gesture:", message)


@app.route('/say_to_file', methods=['POST'])
def say_to_file():

    data = request.json
    message = data.get('message')

    if not message:
        return jsonify({"error": "No message provided"}), 400

    output_file = "/home/nao/audio_LLM.wav"  # File sul robot

    try:
        message_utf8 = message.encode('utf-8')
        print ("Sending message to NAO: ", message_utf8)
        tts.sayToFile(message_utf8, output_file)
        return jsonify({"status": "Message sent to NAO"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
        self.audio_device.setClientPreferences(self.getName(), 16000, 3, 0)  # sample rate of 16000 Hz, channelparam 3 (front channel), and a deinterleaving flag of 0 (only relevant for channelparam 0 (all channels))
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

@app.route("/start_listening", methods=["POST"])
def start_listening():
    # print("Received a request to start listening, current length of server buffer:", len(AudioCapture.buffers))
    rotate_event.clear()
    leds.fadeRGB("FaceLeds", 0x42ff42, 0.5)
    AudioCapture.start_listening()
    return jsonify(success=True)


@app.route("/stop_listening", methods=["POST"])
def stop_listening():
    # print("Received a request to stop listening, current length of server buffer:", len(AudioCapture.buffers))
    leds.off("FaceLeds")
    rotate_event.set()
    rotate_thread = threading.Thread(target=rotate_eyes)
    rotate_thread.start()

    AudioCapture.stop_listening()

    motionProxy.setAngles("HeadPitch", 0, 0.1)
    motionProxy.setAngles("HeadPitch", 0.2, 0.1)
    motionProxy.setAngles("HeadPitch", 0, 0.1)

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
    # print("Received a request to print the length of the server buffer, current length of server buffer:", len(AudioCapture.buffers))
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
                #leds.off("FaceLeds")
                break



def trackFace():

    print ("Starting tracker")

    targetName = "Face"
    faceWidth = 0.6
    trackerProxy.registerTarget(targetName, faceWidth)
    time.sleep(1)
    trackerProxy.track(targetName)
    try:
        while tracking_event.is_set():
            time.sleep(0.5)
    except KeyboardInterrupt:
        print ("Interrupted by user, stopping tracker")
    finally:
        trackerProxy.stopTracker()
        trackerProxy.unregisterAllTargets()

def on_touch_head():
    while tracking_event.is_set():
        # Controlla lo stato dei sensori
        front_touched = memoryProxy.getData("FrontTactilTouched")
        middle_touched = memoryProxy.getData("MiddleTactilTouched")
        rear_touched = memoryProxy.getData("RearTactilTouched")

        if front_touched or middle_touched or rear_touched:
            print("Testa toccata! Interrompo tutte le azioni...")
            requests.post("http://127.0.0.1:6667/idle")
            if(rotate_event.is_set()):
                rotate_event.clear()
            leds.off("FaceLeds")
            motionProxy.stopMove()  # Ferma il movimento
            #postureProxy.goToPosture("Stand", 0.5)
            #lastPose = "Stand"
            tts.stopAll()  # Ferma la voce
            # postureProxy.goToPosture("Stand", 0.5)  # Torna in posizione idle
            print("NAO in stato idle.")

        time.sleep(0.1)


if __name__ == '__main__':

    global lastPose

    import sys

    RED = "\033[91m"  # Codice ANSI per il rosso
    RESET = "\033[0m"  # Resetta il colore

    user_input = raw_input("\n Press " + RED + "ANY BUTTON" + RESET + " for stand up Nao or " + RED + "ENTER" + RESET + " for virtual nao\n")

    if user_input:
        # motionProxy.setStiffnesses("Body", 1)
        postureProxy.goToPosture("Stand", 0.5)  # Assume la posizione in piedi
        lastPose = "Stand"

        touch_head_thread = threading.Thread(target=on_touch_head)
        touch_head_thread.start()

        tracking_event.set()
        track_thread = threading.Thread(target=trackFace)
        track_thread.start()


    try:
        # Avvia il server Flask in un thread separato
        server_thread = threading.Thread(target=lambda: app.run(host='127.0.0.1', port=6666))
        server_thread.daemon = True
        server_thread.start()

        pythonBroker = ALBroker("pythonBroker", "0.0.0.0", 0, NAO_IP, NAO_PORT)  # broker connection: essential for communicating between the module and the NAOqi runtime
        global AudioCapture
        AudioCapture = AudioCaptureModule("AudioCapture")  # create an instance of the AudioCaptureModule class

        print("Premi INVIO per terminare il programma.")
        raw_input()  # Attendi che l'utente prema INVIO

    finally:
        # Interrompi eventi e thread
        print("Chiusura in corso...")
        tracking_event.clear()
        rotate_event.clear()

        motionProxy.stopMove()  # Ferma il movimento
        tts.stopAll()  # Ferma la voce

        leds.off("FaceLeds")
        leds.fadeRGB("FaceLeds", 0xffffff, 0.5)
        motionProxy.rest()

        print("Programma terminato.")