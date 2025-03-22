import speech_recognition as sr

# Inizializza il riconoscitore
recognizer = sr.Recognizer()

# Usa il microfono per catturare l'audio
with sr.Microphone() as source:
    print("Parla ora...")
    recognizer.adjust_for_ambient_noise(source)  # Migliora la qualità dell'audio
    audio = recognizer.listen(source, phrase_time_limit=30, timeout=None)
    text = recognizer.recognize_google(audio, language="it-IT")

    try:
        # Riconoscimento vocale con Google

        print(f"Hai detto: {text}")
    except sr.UnknownValueError:
        print("Non ho capito, riprova.")
    except sr.RequestError as e:
        print(f"Errore nella richiesta a Google: {e}")