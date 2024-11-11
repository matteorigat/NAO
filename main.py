import requests

# URL dell'endpoint request_analysis sul server Gemini
url = "http://localhost:6667/request_analysis"

try:
    # Effettua una richiesta GET per attivare l'analisi dell'immagine
    response = requests.get(url)

    if response.status_code == 200:
        print("Descrizione dell'immagine:", response.json().get("description"))
    else:
        print("Errore:", response.json().get("error", "Errore sconosciuto"))
except Exception as e:
    print("Errore durante la richiesta:", e)