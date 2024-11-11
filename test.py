import os
import base64
import time
import re
import cv2
import numpy as np
import requests
from flask import Flask, request, jsonify
from naoqi import ALProxy

# Configurazione della connessione con il robot NAO
# NAO_IP = "127.0.0.1"

def capture_image():
    #NAO_IP = "192.168.1.166"
    NAO_IP = "127.0.0.1"
    NAO_PORT = 9559

    video_device = ALProxy("ALVideoDevice", NAO_IP, NAO_PORT)
    # subscribe top camera
    AL_kTopCamera = 0
    AL_kQVGA = 2  # 1: 320x240  2: 640x480
    AL_kBGRColorSpace = 13

    capture_device = video_device.subscribeCamera("test", AL_kTopCamera, AL_kQVGA, AL_kBGRColorSpace, 10)

    # create image
    width = 640
    height = 480
    image = np.zeros((height, width, 3), np.uint8)

    # get image
    result = video_device.getImageRemote(capture_device)
    video_device.unsubscribe(capture_device)

    if result == None:
        print 'cannot capture.'
    elif result[6] == None:
        print 'no image data string.'
    else:
        width = result[0]
        height = result[1]
        array = result[6]
        openCV_image = np.ndarray((height, width, 3), dtype=np.uint8, buffer=array)
        #openCV_image = np.ndarray((height, width, 3), "u1", array)
        cv2.imshow("capture", openCV_image)
        cv2.waitKey()


if __name__ == '__main__':
    capture_image()