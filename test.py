import time
import paramiko
from datetime import datetime
from naoqi import ALProxy

# Configurazione della connessione con il robot NAO
#NAO_IP = "127.0.0.1"
NAO_IP = "192.168.1.166"
NAO_PORT = 9559

NAO_USERNAME = "nao"
NAO_PASSWORD = "2468"

def download_file(file_path_on_nao, local_filename):
    try:
        # Crea una connessione SSH con il robot
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(NAO_IP, username=NAO_USERNAME, password=NAO_PASSWORD)

        # Usa SFTP per scaricare il file
        sftp = ssh.open_sftp()
        sftp.get(file_path_on_nao, "./tmp/" +local_filename)  # Scarica il file con il nome locale
        sftp.close()
        ssh.close()

        print("File " + local_filename +" scaricato con successo!")

    except Exception as e:
        print("Errore durante il download del file: ", e)


def detect_silence(audio_proxy):
    audio_proxy.enableEnergyComputation()

    # Soglia di energia per considerare il silenzio
    silence_threshold = 500  # 300 è buono

    # Durata minima del silenzio in secondi
    silence_duration = 2  # Durata del silenzio per considerarlo rilevante

    start_time = time.time()  # Tempo di inizio
    while True:
        # Ottieni l'energia dei microfoni
        front_energy = audio_proxy.getFrontMicEnergy()
        left_energy = audio_proxy.getLeftMicEnergy()
        right_energy = audio_proxy.getRightMicEnergy()
        rear_energy = audio_proxy.getRearMicEnergy()

        # Calcola l'energia media dei microfoni
        average_energy = (front_energy + left_energy + right_energy + rear_energy) / 4.0

        if average_energy < silence_threshold:
            if time.time() - start_time > silence_duration:
                print("Silenzio rilevato!")
                break  # Rilevato il silenzio, esci dal ciclo
        else:
            start_time = time.time()  # Reset del timer se viene rilevato un suono

        time.sleep(0.1)  # Pausa per evitare sovraccarico CPU

def record_audio():
    try:
        audio_proxy = ALProxy("ALAudioDevice", NAO_IP, NAO_PORT)

        filename_audio = "audio_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".wav"
        file_path_on_nao = "/home/nao/recordings/" + filename_audio

        audio_proxy.startMicrophonesRecording(file_path_on_nao)


        detect_silence(audio_proxy)
        print("Registrazione completata.")
        audio_proxy.stopMicrophonesRecording()

        download_file(file_path_on_nao, filename_audio)

    except Exception as e:
        print("Errore durante la registrazione: ", e)

if __name__ == '__main__':
    record_audio()