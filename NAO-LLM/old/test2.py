import requests

# URL del server Flask che sta ascoltando sulla porta 6666
url = 'http://127.0.0.1:6666/gesture'

# Definisci il corpo del messaggio (gesto da eseguire)
message = "Stand"
data = {
    'message': message
}

# Invia la richiesta POST al server
try:
    response = requests.post(url, json=data)
    print(f"Messaggio inviato: {message}")
    print(f"Risposta dal server: {response.json()}")
except Exception as e:
    print(f"Errore: {e}")