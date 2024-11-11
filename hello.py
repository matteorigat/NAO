from naoqi import ALProxy
import time

# Connessione al modulo ALTextToSpeech
tts = ALProxy("ALTextToSpeech", "127.0.0.1", 9559)

# Ciclo infinito per far ripetere il saluto
while True:
    tts.say("Hello, world!")
    time.sleep(2)  # Pausa di 2 secondi tra un saluto e l'altro