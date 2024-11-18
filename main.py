import os
import time
import serverLLM
from flask import Flask

app = Flask(__name__)

def main():

    #os.makedirs("./tmp", exist_ok=True)
    audio_path = "./tmp/received_audio.ogg"

    serverLLM.say("Ciao")
    #serverLLM.say("Ciao, sono Nao, Come posso aiutarti?")

    while True:
        print("Richiesta audio")
        serverLLM.request_audio()
        print("Richiesta audio completata.")
        if os.path.isfile(audio_path):

            print("Analisi audio")
            start_time = time.time()
            response = serverLLM.analyze_audio(audio_path)
            print(f"analyzing took {time.time() - start_time} seconds")

            print("Risposta ricevuta")
            start_time = time.time()
            serverLLM.say(response)
            print(f"saying took {time.time() - start_time} seconds")

            print("Risposta inviata.")
            os.remove(audio_path)




if __name__ == '__main__':
    main()
    app.run(host="127.0.0.1", port=6667)
