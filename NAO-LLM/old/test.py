import threading
import queue
import os
import time
import serverLLM

# Coda condivisa per passare i messaggi tra thread
audio_queue = []

# Thread per registrare l'audio continuamente
def audio_listener():
    while True:
        try:
            audio_file = serverLLM.request_audio()  # Acquisisce l'audio e salva in un file
            if audio_file:
                audio_queue.append(audio_file) # Aggiunge l'audio alla coda
        except Exception as e:
            print(f"Errore nell'ascolto: {e}")


    # Thread per analizzare l'audio e inviare la risposta
def response_handler():
    while True:
        try:
            if audio_queue:
                response = serverLLM.analyze_audio(audio_queue.copy())
                audio_queue.clear()
                serverLLM.say(response)
        except Exception as e:
            print(f"Errore nell'analisi audio: {e}")


if __name__ == '__main__':

    serverLLM.say("Ciao")

    # Avvio dei thread
    listener_thread = threading.Thread(target=audio_listener, daemon=True)
    response_thread = threading.Thread(target=response_handler, daemon=True)

    listener_thread.start()
    response_thread.start()

    # Mantieni il programma attivo
    try:
        while True:
            time.sleep(1)  # Mantiene il programma attivo
    except KeyboardInterrupt:
        print("Terminazione richiesta dall'utente.")