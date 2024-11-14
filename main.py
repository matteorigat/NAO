import os
import time
import serverLLM
from flask import Flask

app = Flask(__name__)

def main():

    #os.makedirs("./tmp", exist_ok=True)
    audio_path = "./tmp/received_audio.ogg"

    serverLLM.say("Ciao, Come posso aiutarti?")

    while True:
        print("Richiesta audio...")
        serverLLM.request_audio()
        print("Richiesta audio completata.")
        if os.path.isfile(audio_path):
            print("Analisi audio")
            response = serverLLM.analyze_audio(audio_path)
            print("Risposta: ", response)
            serverLLM.say(response)
            print("Risposta inviata.")
            os.remove(audio_path)




if __name__ == '__main__':
    app.run(host="127.0.0.1", port=6667)
    main()