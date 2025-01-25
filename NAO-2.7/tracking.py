from naoqi import ALProxy

NAO_IP = "192.168.1.166"
NAO_PORT = 9559

# Connettersi al modulo ALTracker e ALFaceDetection
tracker = ALProxy("ALTracker", NAO_IP, NAO_PORT)
face_detection = ALProxy("ALFaceDetection", NAO_IP, NAO_PORT)

# Inizializzare il tracker (opzionale)
tracker.initialize()

# Registrare il target facciale
face_name = "RedBall"
params = []  # Parametri opzionali per personalizzare il tracking (facoltativo)
tracker.registerTarget(face_name, params)

# Avviare il tracking del volto
tracker.track(face_name)

# Iniziare un ciclo per monitorare il tracking
try:
    while True:
        # Verifica se un volto e stato trovato
        if tracker.isNewTargetDetected():
            position = tracker.getTargetPosition(1)  # Ottieni la posizione nel frame del mondo
            print("Posizione del volto: ", position)

        # Aggiungi altre logiche, come fermare il tracker dopo un certo periodo
except KeyboardInterrupt:
    # Interrompere il tracking quando si desidera fermarlo
    tracker.stopTracker()
    print("Tracker fermato")