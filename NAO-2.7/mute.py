from naoqi import ALProxy

NAO_IP = "192.168.1.166"  # Sostituisci con l'IP del tuo NAO
NAO_PORT = 9559  # Porta predefinita


def zittire_nao():
    try:
        # Crea un proxy per il modulo ALAudioPlayer
        audio_player = ALProxy("ALAudioPlayer", NAO_IP, NAO_PORT)

        # Ferma qualsiasi audio in corso
        audio_player.stopAll()

        print("NAO è stato zittito.")
    except Exception as e:
        print("Errore:", e)

# Esegui la funzione
zittire_nao()