import re
import time
import threading
import requests
from flask import Flask, request, jsonify
from naoqi import ALProxy, ALModule, ALBroker

from Gestures import Happiness1, Happiness2, Happiness3
from Gestures import Sadness1, Sadness2, Sadness3
from Gestures import Anger1, Anger2, Anger3
from Gestures import Fear1, Fear2, Fear3
from Gestures import Sadness3reverse, Fear3reverse

# Configurazione del server Flask
app = Flask(__name__)

# Configurazione della connessione con il robot NAO
NAO_IP = "127.0.0.1"
#NAO_IP = "192.168.1.166"
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

@app.route('/say', methods=['POST'])
def say():
    rotate_event.clear()
    leds.fadeRGB("FaceLeds", 0xffffff, 0.2)

    data = request.json
    message = data.get('message')

    if not message:
        return jsonify({"error": "No message provided"}), 400

    #configuration = {"bodyLanguageMode": "random"}

    segments = re.split(r'(\[.*?\])', message)

    try:
        for segment in segments:
            # Prima di ogni segmento, invia il tag (se presente)
            if segment.startswith("[") and segment.endswith("]"):
                if segment[1:-1] == "rst":
                    gesture("Stand")
                    continue
                if segment[1:-1] == "happy":
                    gesture("Happiness1")  # Invio del tag
                elif segment[1:-1] == "sad":
                    gesture("Sadness1")
                elif segment[1:-1] == "fear":
                    gesture("Fear1")
                elif segment[1:-1] == "angry":
                    gesture("Anger1")
                print("sent tag: " + segment[1:-1])

            elif segment.strip():
                # Pronuncia il segmento
                #tts.stopAll()
                message_utf8 = segment.encode('utf-8')
                print ("Sending message to NAO: ", message_utf8)
                tts.say(message_utf8)

        return jsonify({"status": "Message sent to NAO"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def gesture(message):

    if not message:
        return

    if message == "start":
        postureProxy.goToPosture("Stand", 0.5)
        return

    global lastPose
    if(message == "Stand" and lastPose != "Stand"):
        return goToStand()

    # Controlla se il messaggio corrisponde a un gesto valido
    gesture_class = GESTURE_MAP.get(message)
    if not gesture_class:
        return

    lastPose = message

    gesture_class.execute_gesture(NAO_IP, NAO_PORT)

def goToStand():
    global lastPose
    reverse = False

    if (lastPose == "Sadness3" or lastPose == "Fear3"):
        lastPose += "reverse"
        reverse = True

    gesture_class = GESTURE_MAP.get(lastPose)
    if not gesture_class:
        return

    if reverse:
        gesture_class.execute_gesture(NAO_IP, NAO_PORT)
    else:
        gesture_class.execute_gesture(NAO_IP, NAO_PORT, reverse=True)

    # posture.goToPosture("Stand", 0.5)
    lastPose = "Stand"



# @app.route('/capture_image', methods=['GET'])
# def capture_image():
#     video_device = ALProxy("ALVideoDevice", NAO_IP, NAO_PORT)
# 
#     AL_kTopCamera = 0
#     AL_kQVGA = 2  # 1: 320x240  2: 640x480
#     AL_kBGRColorSpace = 13
# 
#     capture_device = video_device.subscribeCamera("test", AL_kTopCamera, AL_kQVGA, AL_kBGRColorSpace, 10)
# 
#     # get image
#     result = video_device.getImageRemote(capture_device)
#     video_device.unsubscribe(capture_device)
# 
#     if result == None:
#         return jsonify({"error": "Cannot capture."}), 500
#     elif result[6] == None:
#         return jsonify({"error": "No image data string."}), 500
# 
#     try:
#         width = result[0]
#         height = result[1]
#         array = result[6]
#         print("Image size: ", width, height)
# 
#         # Convert to OpenCV image
#         openCV_image = np.ndarray((height, width, 3), dtype=np.uint8, buffer=array)
# 
#         # Optionally, show the image (for debugging)
#         #cv2.imshow("capture", openCV_image)
#         #cv2.waitKey(1)  # Prevent the window from freezing
# 
#         # Convert to base64
#         _, buffer = cv2.imencode('.jpg', openCV_image)  # Convert image to .jpg format
#         image_base64 = base64.b64encode(buffer).decode('utf-8')
# 
#         print("Image sent to client:", image_base64[:50])  # Print first 50 chars of the base64 string
#         return jsonify({"image": image_base64}), 200
# 
#     except Exception as e:
#         return jsonify({"error": "Failed to process image: {}".format(str(e))}), 500


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
    leds.off("FaceLeds")
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


def trackFace():

    print ("Starting tracker")

    targetName = "Face"
    faceWidth = 0.6
    trackerProxy.registerTarget(targetName, faceWidth)

    trackerProxy.track(targetName)
    try:
        while tracking_event.is_set():
            time.sleep(1)
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

    user_input = raw_input("\nPress any button for stand up NAO\n")

    if user_input:
        # motionProxy.setStiffnesses("Body", 1)
        postureProxy.goToPosture("Stand", 0.5)  # Assume la posizione in piedi
        lastPose = "Stand"

        tracking_event.set()
        track_thread = threading.Thread(target=trackFace)
        track_thread.start()

        touch_head_thread = threading.Thread(target=on_touch_head)
        touch_head_thread.start()


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