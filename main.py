import os
import base64
import time
import re
import cv2
import numpy as np
import requests
from flask import Flask, request, jsonify
from naoqi import ALProxy

# Configurazione del server Flask
app = Flask(__name__)

# Configurazione della connessione con il robot NAO
#NAO_IP = "127.0.0.1"
NAO_IP = "192.168.1.166"
NAO_PORT = 9559


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
        clean_msg = clean_message(message)
        clean_msg_utf8 = clean_msg.encode('utf-8')
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


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=6666)