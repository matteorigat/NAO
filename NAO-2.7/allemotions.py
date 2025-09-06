from naoqi import ALProxy
import time
import sys
import threading
from Gestures import Happiness1, Happiness2, Happiness3
from Gestures import Sadness1, Sadness2, Sadness3
from Gestures import Anger1, Anger2, Anger3
from Gestures import Fear1, Fear2, Fear3
from Gestures import Sadness3reverse, Fear3reverse


#NAO_IP = "192.168.1.166"
NAO_IP = "127.0.0.1"
NAO_PORT = 9559

GESTURES = [
    {"name": "Happiness1", "class": Happiness1},
    {"name": "Happiness2", "class": Happiness2},
    {"name": "Happiness3", "class": Happiness3},
    {"name": "Sadness1", "class": Sadness1},
    {"name": "Sadness2", "class": Sadness2},
    {"name": "Sadness3", "class": Sadness3},
    {"name": "Anger1", "class": Anger1},
    {"name": "Anger2", "class": Anger2},
    {"name": "Anger3", "class": Anger3},
    {"name": "Fear1", "class": Fear1},
    {"name": "Fear2", "class": Fear2},
    {"name": "Fear3", "class": Fear3},
]

def main():
    """Main entry point."""

    try:
        motionProxy = ALProxy("ALMotion", NAO_IP, NAO_PORT)
        postureProxy = ALProxy("ALRobotPosture", NAO_IP, NAO_PORT)
    except Exception as e:
        print(f"Errore durante la connessione ai proxy NAOqi: {e}")
        sys.exit(1)

    current_gesture_index = 0

    try:
        while True:
            raw_input("Premi INVIO per eseguire la prossima emozione...")

            # Esegui l'emozione corrente
            current_gesture = GESTURES[current_gesture_index]
            print(f"Esecuzione: {current_gesture['name']}")
            current_gesture['class'].execute_gesture(NAO_IP, NAO_PORT)

            # Torna in posizione "Stand"
            print("Torno in posizione Stand...")
            postureProxy.goToPosture("Stand", 0.5)
            time.sleep(1.0)  # Lascia un po' di tempo per la transizione

            # Aggiorna l'indice per la prossima emozione
            current_gesture_index = (current_gesture_index + 1) % len(GESTURES)

    except KeyboardInterrupt:
        print("\nInterruzione manuale. Fermo il robot.")
    finally:
        print("Riposo il robot...")
        motionProxy.rest()
        print("Programma terminato.")

if __name__ == "__main__":
    main()