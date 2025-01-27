import socket
import speech_recognition as sr
import pyttsx3
import time
import dlib
import cv2
import serverLLM
from playsound import playsound
import threading


# Funzione per inviare messaggi al server
def send_message(message):
    host = '127.0.0.1'  # Indirizzo IP del server (localhost per Unity)
    port = 65432  # Porta del server (deve corrispondere a quella in Unity)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(message.encode('utf-8'))
            #print(f"Messaggio inviato: {message}")
    except Exception as e:
        print(f"Errore: {e}")


def listen_to_microphone():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    # Acquisisce l'audio dal microfono
    with microphone as source:
        print("Listening...")
        send_message("listening")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    # Prova a riconoscere il testo in italiano
    try:
        print("Riconoscimento in corso...")
        text = recognizer.recognize_google(audio, language="it-IT")  # Imposta la lingua italiana
        print(f"Testo riconosciuto: {text}")
        send_message("loading")
        return text
    except sr.UnknownValueError:
        print("Non ho capito, per favore riprova.")
        return None
    except sr.RequestError as e:
        print(f"Errore con il servizio di riconoscimento vocale; {e}")
        return None


def face_tracking():
    detector = dlib.get_frontal_face_detector()  # Rilevatore di volti
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()  # Legge un frame dalla fotocamera
        if not ret:
            print("Errore nell'accesso alla fotocamera.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)  # Rileva i volti

        for face in faces:
            # Calcola il centro del volto
            center_x = (face.left() + face.right()) // 2
            center_y = (face.top() + face.bottom()) // 2

            # Invia le coordinate del centro del volto
            face_data = f"{center_x},{center_y}"
            send_message(f"face_position:{face_data}")


        # Mostra il feed della videocamera
        #cv2.imshow("Face Tracking", frame)


        # Esce se premi 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

class TextToSpeech:
    def __init__(self, language="it-IT"):
        self.engine = pyttsx3.init()  # Inizializza il motore una sola volta
        self.engine.setProperty('rate', 150)  # Imposta la velocità della voce
        self.engine.setProperty('volume', 1)  # Imposta il volume (0.0 a 1.0)


    def speak(self, text):
        """Pronuncia il testo in italiano."""
        self.engine.say(text)  # Pronuncia il testo
        self.engine.runAndWait()  # Esegui la sintesi vocale


def main():
    tts = TextToSpeech()

    while True:
        # Ascolta il microfono
        send_message("listening")
        text = listen_to_microphone()

        if text:
            # Elabora il testo
            send_message("loading")
            processed_text = serverLLM.analyze_text(text)

            response = serverLLM.say_to_file(processed_text)

            if response:
                send_message("speaking")
                playsound(response)


if __name__ == "__main__":
    face_tracking_thread = threading.Thread(target=face_tracking)
    main_thread = threading.Thread(target=main)

    # Imposta entrambi i thread come daemon per chiuderli automaticamente quando il programma termina
    face_tracking_thread.daemon = True
    main_thread.daemon = True

    # Avvia i thread
    face_tracking_thread.start()
    main_thread.start()

    # Mantieni il programma principale attivo fino a quando l'utente non termina
    face_tracking_thread.join()
    main_thread.join()