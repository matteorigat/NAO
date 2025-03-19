from flask import Flask, request, jsonify
from naoqi import ALProxy, ALModule, ALBroker
import threading
import time
from Gestures import Happiness1, Happiness2, Happiness3
from Gestures import Sadness1, Sadness2, Sadness3
from Gestures import Anger1, Anger2, Anger3
from Gestures import Fear1, Fear2, Fear3
from Gestures import Sadness3reverse, Fear3reverse


app = Flask(__name__)

NAO_IP = "192.168.1.166"
#NAO_IP = "127.0.0.1"
NAO_PORT = 9559

postureProxy = ALProxy("ALRobotPosture", NAO_IP, NAO_PORT)
motionProxy = ALProxy("ALMotion", NAO_IP, NAO_PORT)

lastPose = "Stand"

GESTURE_MAP = {
    "Anger1": Anger1, "Anger2": Anger2, "Anger3": Anger3,
    "Fear1": Fear1, "Fear2": Fear2, "Fear3": Fear3,
    "Happiness1": Happiness1, "Happiness2": Happiness2, "Happiness3": Happiness3,
    "Sadness1": Sadness1, "Sadness2": Sadness2, "Sadness3": Sadness3,
    "Sadness3reverse": Sadness3reverse, "Fear3reverse": Fear3reverse
}

@app.route('/gesture', methods=['POST'])
def gesture():
    data = request.json
    message = data.get('message')

    if not message:
        return jsonify({"error": "No message provided"}), 400

    if message == "start":
        postureProxy.goToPosture("Stand", 0.5)
        return jsonify({"message": "Gesture executed"}), 200

    global lastPose
    if(message == "Stand" and lastPose != "Stand"):
        return goToStand()

    # Controlla se il messaggio corrisponde a un gesto valido
    gesture_class = GESTURE_MAP.get(message)
    if not gesture_class:
        return jsonify({"error": "Invalid gesture name " + message}), 400

    lastPose = message

    gesture_class.execute_gesture(NAO_IP, NAO_PORT)

    return jsonify({"message": "Gesture executed"}), 200

def goToStand():
    #posture = ALProxy("ALRobotPosture", NAO_IP, NAO_PORT)
    #posture.goToPosture("Stand", 0.5)

    global lastPose
    reverse = False

    if (lastPose == "Sadness3" or lastPose == "Fear3"):
        lastPose += "reverse"
        reverse = True

    gesture_class = GESTURE_MAP.get(lastPose)
    if not gesture_class:
        return jsonify({"error": "Invalid reverse gesture name " + lastPose}), 400

    if reverse:
        gesture_class.execute_gesture(NAO_IP, NAO_PORT)
    else:
        gesture_class.execute_gesture(NAO_IP, NAO_PORT, reverse=True)

    lastPose = "Stand"

    return jsonify({"message": "Gesture executed"}), 200



if __name__ == "__main__":

    try:
        # Avvia il server Flask in un thread separato
        server_thread = threading.Thread(target=lambda: app.run(host='127.0.0.1', port=6666))
        server_thread.daemon = True
        server_thread.start()


        print("Premi INVIO per terminare il programma.")
        raw_input()  # Attendi che l'utente prema INVIO

    finally:
        motionProxy.rest()

        print("Programma terminato.")