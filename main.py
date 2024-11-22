import os
import time
import serverLLM
from flask import Flask

app = Flask(__name__)

def main():


    serverLLM.say("Ciao")
    #serverLLM.say("Ciao, sono Nao, Come posso aiutarti?")

    while True:
        print("Richiesta audio")
        start_time = time.time()
        file = serverLLM.request_audio()
        print(f"entire audio requesting took {time.time() - start_time} seconds")
        if file:

            print("Analisi audio")
            start_time = time.time()
            response = serverLLM.analyze_audio(file)
            print(f"analyzing took {time.time() - start_time} seconds")

            print("Risposta ricevuta")
            start_time = time.time()
            serverLLM.say(response)
            print(f"saying took {time.time() - start_time} seconds")




if __name__ == '__main__':
    main()
    app.run(host="127.0.0.1", port=6667)
