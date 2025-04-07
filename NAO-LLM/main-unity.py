import socket
import re
import os
import time
import speech_recognition as sr
import pyttsx3
import cv2
import serverLLM
from playsound import playsound
import threading
import subprocess
import json

dialogue_path = "objective 1/results_virtual/dialogue_virtual_" + time.strftime("%d-%m-%Y_%H-%M-%S") + ".json"

lastPose = "Stand"

# Funzione per inviare messaggi al server
def send_message(message):
    host = '127.0.0.1'  # Indirizzo IP del server (localhost per Unity)
    port = 47777  # Porta del server (deve corrispondere a quella in Unity)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(message.encode('utf-8'))
            if(not ("face_position" in message)):
                print(f"Messaggio inviato: {message}")
    except Exception as e:
        #print(f"Errore: {e}")
        pass


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
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if not tracking_face:
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            if len(faces) > 0:
                x, y, w, h = faces[0]
                tracker = cv2.TrackerCSRT_create()
                tracker.init(frame, (x, y, w, h))
                tracking_face = True
                print("Face detected and tracking started.")
        else:
            success, bbox = tracker.update(frame)
            if success:
                x, y, w, h = [int(v) for v in bbox]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                center_x = x + w // 2
                center_y = y + h // 2
                target_position = (center_x, center_y)  # update the target position
                last_position = target_position  # update last position with the effective tracking position
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

# class TextToSpeech:
#     def __init__(self, language="it-IT"):
#         self.engine = pyttsx3.init()  # Inizializza il motore
#         self.engine.setProperty('rate', 160)  # Velocità della voce
#         self.engine.setProperty('volume', 1)  # Volume massimo
#
#         # Imposta la voce italiana
#         voices = self.engine.getProperty('voices')
#         for voice in voices:
#             if "Shelley (Italiano (Italia))" in voice.name:
#                 self.engine.setProperty('voice', voice.id)
#                 break
#
#     def speak(self, text):
#         """Pronuncia il testo in italiano."""
#         self.engine.say(text)  # Pronuncia il testo
#         self.engine.runAndWait()  # Esegui la sintesi vocale
#
#
# def speak_local_tts(tts, text):
#     global lastPose
#     segments = re.split(r'(\[.*?\])', text)
#
#     for segment in segments:
#         # Prima di ogni segmento, invia il tag (se presente)
#         if segment.startswith("[") and segment.endswith("]"):
#             tag = segment[1:-1]
#             if tag == "rst" and lastPose != "Stand":
#                 send_message("Stand")
#                 lastPose = "Stand"
#                 time.sleep(2)
#             elif tag == "happy" and lastPose != "Happinesss1":
#                 send_message("Happiness1")  # Invio del tag
#                 lastPose = "Happiness1"
#             elif tag == "sad" and lastPose != "Sadness1":
#                 send_message("Sadness1")
#                 lastPose = "Sadness1"
#             elif tag == "fear" and lastPose != "Fear1":
#                 send_message("Fear1")
#                 lastPose = "Fear1"
#             elif tag == "angry" and lastPose != "Anger1":
#                 send_message("Anger1")
#                 lastPose = "Anger1"
#             #print("sent tag: " + segment[1:-1])
#
#         elif segment.strip():
#             # Pronuncia il segmento
#             print(f"Segmento: {segment}")
#             tts.speak(segment)
#
#     if(lastPose != "Stand"):
#         send_message("Stand")



def load_dialogue(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "id": count_json_files(),  # ID progressivo basato sui file esistenti
            "interaction": "virtual",
            "history": []  # Lista vuota per la conversazione
        }  # Inizializza con una lista di storia vuota


def save_dialogue(dialogue):
    with open(dialogue_path, "w", encoding="utf-8") as f:
        json.dump(dialogue, f, indent=4, ensure_ascii=False)

def count_json_files():
    results_dir = 'objective 1/results_virtual/'
    files = os.listdir(results_dir)
    json_files = [file for file in files if file.endswith('.json')]
    return len(json_files)


def listen_to_microphone(dialogue):
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 1.5
    microphone = sr.Microphone()

    audio_data = None
    audio_path_wav = "./tmp/received_audio.wav"
    audio_path = "./tmp/received_audio.ogg"

    while True:
        if audio_data is None:
            print("Listening...")
            send_message("listening")
            start_time = time.time()

            with microphone as source:
                try:
                    #recognizer.adjust_for_ambient_noise(source)
                    audio_data = recognizer.listen(source, phrase_time_limit=30, timeout=None)
                    text = recognizer.recognize_google(audio_data, language="it-IT")
                    print("testo audio riconosciuto: " + text)
                except Exception as e:
                    audio_data = None
                    continue

                if not text.strip() or time.time() - start_time < 1.0:
                    audio_data = None
                    continue

                dialogue["history"].append({"role": "user", "content": text})
                save_dialogue(dialogue)  # Salva immediatamente dopo l'input dell'utente
                print(f"Recording took {time.time() - start_time} seconds")

                start_time = time.time()

                with open(audio_path_wav, "wb") as f:
                    f.write(audio_data.get_wav_data())

                    serverLLM.convert_to_ogg(audio_path_wav, audio_path)

                    print(f"Processing audio took {time.time() - start_time} seconds")

                    uploader = serverLLM.upload_to_gemini_threaded(audio_path, mime_type="audio/ogg")

                    return uploader, dialogue


def speak_and_send_tags(text):
    global lastPose
    segments = re.split(r'(\[.*?\])', text)

    for segment in segments:
        # Prima di ogni segmento, invia il tag (se presente)
        if segment.startswith("[") and segment.endswith("]"):
            tag = segment[1:-1]
            if tag == "rst" and lastPose != "Stand":
                send_message("Stand")
                lastPose = "Stand"
                time.sleep(2)
            elif tag == "happy" and lastPose != "Happinesss1":
                send_message("Happiness1")  # Invio del tag
                lastPose = "Happiness1"
            elif tag == "sad" and lastPose != "Sadness1":
                send_message("Sadness1")
                lastPose = "Sadness1"
            elif tag == "fear" and lastPose != "Fear1":
                send_message("Fear1")
                lastPose = "Fear1"
            elif tag == "angry" and lastPose != "Anger1":
                send_message("Anger1")
                lastPose = "Anger1"
            # print("sent tag: " + segment[1:-1])

        elif segment.strip():
            # Pronuncia il segmento
            #print(f"Segmento: {segment}")
            response = serverLLM.say_to_file(segment.strip())
            if response:
                playsound(response)

    if (lastPose != "Stand"):
        send_message("Stand")
        time.sleep(2)



def main():
    #tts = TextToSpeech()

    global dialogue_path
    dialogue = load_dialogue(dialogue_path)

    response = serverLLM.say_to_file("Ciao")
    if response:
        playsound(response)
    #speak_local_tts(tts, "Ciao")

    while True:
        # Ascolta il microfono
        send_message("listening")
        uploader, dialogue = listen_to_microphone(dialogue)

        if uploader:
            # Elabora il testo
            send_message("loading")
            processed_text = serverLLM.analyze_audio(uploader)

            dialogue["history"].append({"role": "system", "content": processed_text})
            save_dialogue(dialogue)
            print(processed_text)

            # Sincronizza i tag con la lettura del testo
            send_message("speaking")
            speak_and_send_tags(processed_text)
            #speak_local_tts(tts, processed_text)
                
            


if __name__ == "__main__":
    if not os.path.exists("tmp"):
        os.makedirs("tmp")

    facetracking_thread = threading.Thread(target=face_tracking)

    facetracking_thread.daemon = True
    facetracking_thread.start()

    main()

    facetracking_thread.join()