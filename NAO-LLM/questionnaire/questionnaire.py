from flask import Flask, render_template, request, json

app = Flask(__name__)

domande = [
    {"testo": "Mi vedo come una persona riservata", "id": "riservata", "obbligatoria": True},
    {"testo": "Mi vedo come una persona che generalmente si fida", "id": "si_fida", "obbligatoria": True},
    {"testo": "Mi vedo come una persona che tende a essere pigra", "id": "pigra", "obbligatoria": True},
    {"testo": "Mi vedo come una persona rilassata e che sopporta bene lo stress", "id": "rilassata", "obbligatoria": True},
    {"testo": "Mi vedo come una persona con pochi interessi artistici", "id": "interessi_artistici", "obbligatoria": True},
    {"testo": "Mi vedo come una persona spigliata e socievole", "id": "spigliata", "obbligatoria": True},
    {"testo": "Mi vedo come una persona che tende a trovare i difetti negli altri", "id": "difetti_negli_altri", "obbligatoria": True},
    {"testo": "Mi vedo come una persona coscienziosa nel lavoro", "id": "coscienziosa", "obbligatoria": True},
    {"testo": "Mi vedo come una persona che si agita facilmente", "id": "agita_facilmente", "obbligatoria": True},
    {"testo": "Mi vedo come una persona con una fervida immaginazione", "id": "fervida_immaginazione", "obbligatoria": True},
]

def normalizza(val):
    return (val - 2) / (10 - 2) # Normalizzazione tra 0 e 1, dato che i punteggi vanno da 2 a 10

# Funzione per calcolare il punteggio per ciascuna dimensione della personalità
def calcola_punteggio_big_five(punteggi):
    # Le dimensioni sono mappate come segue:
    # Agreeableness (2, 7_re)
    # Conscientiousness (3_re, 8)
    # Emotional stability (4, 9_re)
    # Extroversion: (1_re, 6)
    # Openness: (5_re, 10)

    # Calcolare il punteggio grezzo per ciascuna dimensione, tenendo conto degli item invertiti (reverse scored)
    punteggio = {
        'Agreeableness': (punteggi[1] + (6 - punteggi[6])),
        'Conscientiousness': ((6 - punteggi[2]) + punteggi[7]),
        'Emotional stability': (punteggi[3] + (6 - punteggi[8])),
        'Extroversion': ((6 - punteggi[0]) + punteggi[5]),
        'Openness': ((6 - punteggi[4]) + punteggi[9])
    }

    # Normalizzare ogni punteggio da 0 a 1
    punteggio_normalizzato = {key: normalizza(valore) for key, valore in punteggio.items()}

    return punteggio_normalizzato
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        risposte = {domanda["id"]: request.form.get(domanda["id"]) for domanda in domande}
        if any(domanda["obbligatoria"] and not risposte[domanda["id"]] for domanda in domande):
            return "Errore: rispondi a tutte le domande obbligatorie.", 400

        punteggi_big_five = calcola_punteggio_big_five([int(risposta) for risposta in risposte.values()])

        with open("../tmp/big_five_scores.json", "w") as f:
            json.dump(punteggi_big_five, f, indent=4)
        return render_template("index.html", completato=True)

    return render_template("index.html", domande=domande)

if __name__ == "__main__":
    app.run(debug=True)