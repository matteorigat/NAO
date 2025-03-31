import os
import time
import serverLLM
import threading
from flask import Flask
import json

app = Flask(__name__)
uploader = None

dialogue_path = "objective 1/results_real/dialogue_real_" + time.strftime("%d-%m-%Y_%H-%M-%S") + ".json"

def load_dialogue(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "id": count_json_files(),  # ID progressivo basato sui file esistenti
            "interaction": "real",
            "history": []  # Lista vuota per la conversazione
        }  # Inizializza con una lista di storia vuota


def save_dialogue(dialogue):
    with open(dialogue_path, "w", encoding="utf-8") as f:
        json.dump(dialogue, f, indent=4, ensure_ascii=False)

def count_json_files():
    results_dir = 'objective 1/results_real/'
    files = os.listdir(results_dir)
    json_files = [file for file in files if file.endswith('.json')]
    return len(json_files)

def main():
    global dialogue_path
    dialogue = load_dialogue(dialogue_path)


    serverLLM.say("Ciao")
    #serverLLM.say("Ciao, sono Nao, Come posso aiutarti?")
    dialogue["history"].append({"role": "system", "content": "Ciao"})

    while True:
        try:
            global uploader
            uploader, audio_text = serverLLM.request_audio()
            dialogue["history"].append({"role": "user", "content": audio_text})
            if uploader:
                response = serverLLM.analyze_audio(uploader)
                dialogue["history"].append({"role": "system", "content": response})
                save_dialogue(dialogue)
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
