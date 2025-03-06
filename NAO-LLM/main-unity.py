import socket
import speech_recognition as sr
import pyttsx3
import cv2
import serverLLM
from playsound import playsound
import threading


# Funzione per inviare messaggi al server
def send_message(message):
    host = '127.0.0.1'  # Indirizzo IP del server (localhost per Unity)
    port = 50000  # Porta del server (deve corrispondere a quella in Unity)

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
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Initialize the video capture object
    cap = cv2.VideoCapture(0)  # Use 0 for the default webcam

    # Initialize the tracker variable
    tracker = None
    tracking_face = False

    # Ottieni la larghezza e l'altezza della finestra del video
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"Risoluzione della finestra video: {frame_width}x{frame_height}")

    while True:
        # Read a frame from the video capture
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        # Convert the frame to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if not tracking_face:
            # Detect faces in the grayscale frame
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) > 0:
                # Select the first detected face (you can modify this to select a specific face)
                x, y, w, h = faces[0]
                tracker = cv2.TrackerCSRT_create()
                tracker.init(frame, (x, y, w, h))
                tracking_face = True
                print("Face detected and tracking started.")
        else:
            # Update the tracker
            success, bbox = tracker.update(frame)
            if success:
                # Draw a rectangle around the tracked face
                x, y, w, h = [int(v) for v in bbox]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                center_x = x + w // 2
                center_y = y + h // 2
                send_message(f"face_position:{center_x},{center_y}")

            else:
                tracking_face = False
                print("Lost track of the face. Re-detecting.")
                tracker = None

        # # Display the resulting frame
        # cv2.imshow('Face Tracking', frame)
        # 
        # # Break the loop if the 'q' key is pressed
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

    # Release the video capture object and close all OpenCV windows
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
    #tts = TextToSpeech()

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
    main_thread = threading.Thread(target=main)

    main_thread.daemon = True
    main_thread.start()

    face_tracking()

    main_thread.join()