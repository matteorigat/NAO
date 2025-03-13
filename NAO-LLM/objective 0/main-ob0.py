from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import uuid
import os
import time
import socket
import random

import serverLLM

app = Flask(__name__)
app.secret_key = os.urandom(24)

gestures_dict = {
        "happiness": ["Happiness1", "Happiness2", "Happiness3"],
        "sadness": ["Sadness1", "Sadness2", "Sadness3"],
        "anger": ["Anger1", "Anger2", "Anger3"],
        "fear": ["Fear1", "Fear2", "Fear3"]
    }

welcome_int = -1
gestures_list = [[], []]


feedback_dir = "results"
if not os.path.exists(feedback_dir):
    os.makedirs(feedback_dir)

# Funzione per generare il nome del file (per sessione unica)
def generate_filename():
    return os.path.join(feedback_dir, "feedback_" + time.strftime("%d-%m-%Y_%H-%M-%S") + ".json")

# Funzione per caricare i feedback esistenti dal file JSON
def load_feedback(filepath):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Funzione per salvare i feedback nel file JSON
def save_feedback(feedback, filepath):
    with open(filepath, "w") as f:
        json.dump(feedback, f, indent=4)

def count_json_files():
    results_dir = 'results'
    files = os.listdir(results_dir)
    json_files = [file for file in files if file.endswith('.json')]
    return len(json_files)

def send_message(message):
    global welcome_int
    if welcome_int == 0:
        host = '127.0.0.1'  # Indirizzo IP del server (localhost per Unity)
        port = 50000  # Porta del server (deve corrispondere a quella in Unity)


        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                s.sendall(message.encode('utf-8'))
                print(f"Messaggio inviato virtual: {message}")
        except Exception as e:
            print(f"Errore: {e}")
    elif welcome_int == 1:
        serverLLM.send_gesture(message)
        print(f"Messaggio inviato real: {message}")


def open_window():
    if welcome_int == 0:
        return render_template("virtual.html")
    elif welcome_int == 1:
        return render_template("real.html")


@app.route('/')
def index():
    global welcome_int

    if welcome_int != -1:
        return open_window()
    else:
        if random.choice([True, False]):
            welcome_int = 1
        else:
            welcome_int = 0

    global gestures_list
    gestures_list = [[], []]


    # Crea una copia della lista di gesture per non modificarla mentre selezioni
    remaining_gestures = {emotion: gestures.copy() for emotion, gestures in gestures_dict.items()}

    # Aggiungi almeno una gesture per emozione a ciascuna lista
    for emotion, gestures in remaining_gestures.items():
        if len(gestures) > 1:  # Verifica che ci siano abbastanza gesture
            # Seleziona due gesture e rimuovile dalla lista
            chosen_gesture1 = random.choice(gestures)
            gestures.remove(chosen_gesture1)
            chosen_gesture2 = random.choice(gestures)
            gestures.remove(chosen_gesture2)

            gestures_list[0].append(chosen_gesture1)
            gestures_list[1].append(chosen_gesture2)

    # Mescola le gesture rimanenti da distribuire tra le due liste
    remaining_gestures_flat = [gesture for gestures_list in remaining_gestures.values() for gesture in
                               gestures_list]
    random.shuffle(remaining_gestures_flat)

    # Distribuisci le gesture rimanenti nelle due liste in modo bilanciato
    while remaining_gestures_flat:
        if len(gestures_list[0]) <= len(gestures_list[1]):
            gestures_list[0].append(remaining_gestures_flat.pop())
        else:
            gestures_list[1].append(remaining_gestures_flat.pop())

    random.shuffle(gestures_list[0])
    random.shuffle(gestures_list[1])

    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())  # Assegna un ID univoco all'utente

    filepath = generate_filename()
    number = count_json_files()

    feedback = {"id": number}
    save_feedback(feedback, filepath)

    session['filepath'] = filepath

    return open_window()

@app.route('/questions')
def questions():
    send_message("Stand")
    time.sleep(5)
    send_message(gestures_list[welcome_int][0])
    return render_template("questions.html")

@app.route('/repeat', methods=['POST'])
def repeat():
    send_message("Stand")
    time.sleep(5)
    send_message(gestures_list[welcome_int][0])
    return jsonify({"message": "Ripetizione eseguita"}), 200


@app.route('/thanks')
def thanks():
    return render_template("thanks.html")


@app.route('/submit', methods=['POST'])
def submit():

    global welcome_int
    # Controlla se l'utente ha un ID (assegnato al momento dell'accesso)
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "ID utente mancante"}), 400

    # Estrai i dati inviati dal client (emoji e i due valori SAM)
    data = request.json

    emoji = data.get("emotion")
    sam = data.get("valence")  # Felicità
    sam2 = data.get("arousal")  # Eccitazione


    if emoji and sam and sam2:
        # Usa il filepath della sessione
        filepath = session.get('filepath')

        # Carica i feedback esistenti dal file
        feedback = load_feedback(filepath)

        # Se l'utente non ha già un campo nel file, lo inizializziamo
        if user_id not in feedback:
            feedback[user_id] = []

        # Aggiungi il nuovo feedback nella lista dell'utente
        feedback[user_id].append({
            "interaction": "virtual" if welcome_int == 0 else "real",
            "emotion": gestures_list[welcome_int][0],
            "emotion-recognized": emoji,
            "valence": sam,
            "arousal": sam2
        })

        # Salva il feedback nel file
        save_feedback(feedback, filepath)

        gestures_list[welcome_int].pop(0)

        if len(gestures_list[welcome_int]) == 0:
            if welcome_int == 0:
                welcome_int = 1
            elif welcome_int == 1:
                welcome_int = 0

            if len(gestures_list[0]) == 0 and len(gestures_list[1]) == 0:
                return jsonify({"message": "Change window."}), 308
            return jsonify({"message": "Change window."}), 303

        else:
            send_message(gestures_list[welcome_int][0])



        # Restituisci una risposta positiva
        return jsonify({"message": "Feedback ricevuto!"}), 200

    return jsonify({"error": "Dati incompleti"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True)