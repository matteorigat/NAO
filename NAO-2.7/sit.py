from naoqi import ALProxy

# Configurazione
NAO_IP = "192.168.1.166"  # Sostituisci con l'IP del tuo NAO
NAO_PORT = 9559  # Porta predefinita

try:
    # Creazione dei proxy
    motion = ALProxy("ALMotion", NAO_IP, NAO_PORT)
    posture = ALProxy("ALRobotPosture", NAO_IP, NAO_PORT)

    # Risveglio del robot
    motion.wakeUp()

    # Far alzare il robot in posizione eretta
    posture.goToPosture("Stand", 0.5)

    # Attendi qualche secondo
    import time
    time.sleep(1)

    # Far sedere il robot
    #posture.goToPosture("Crouch", 0.5)

    # Disattivazione dei motori (per risparmiare energia)
    motion.rest()

    print("Script completato con successo.")

except Exception as e:
    print("Errore: ", e)