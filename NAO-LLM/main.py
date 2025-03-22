import os
import time
import serverLLM
import threading
from flask import Flask

app = Flask(__name__)
uploader = None

def main():
    serverLLM.say("Ciao")
    #serverLLM.say("Ciao, sono Nao, Come posso aiutarti?")

    while True:
        try:
            global uploader
            uploader = serverLLM.request_audio()
            if uploader:
                response = serverLLM.analyze_audio(uploader)
                serverLLM.say(response)
        except Exception as e:
            if "Idle" in str(e):
                continue

            print(f"Errore durante l'analisi audio: {e}")
            return
        finally:
            uploader = None



@app.route('/idle', methods=['POST'])
def idle():
    global uploader
    try:
        uploader.stopRequest = True
    finally:
        return "Idle request received", 200




if __name__ == '__main__':
    audio_thread = threading.Thread(target=main)
    audio_thread.daemon = True  # Questo permette al thread di terminare quando il programma principale termina
    audio_thread.start()

    app.run(host="127.0.0.1", port=6667)
