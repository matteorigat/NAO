import socket
import speech_recognition as sr
import pyttsx3
import time
import serverLLM
from playsound import playsound


# Funzione per inviare messaggi al server
def send_message(message):
    host = '127.0.0.1'  # Indirizzo IP del server (localhost per Unity)
    port = 65432  # Porta del server (deve corrispondere a quella in Unity)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(message.encode('utf-8'))
            print(f"Messaggio inviato: {message}")
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
    main()