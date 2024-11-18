import requests
import numpy as np
import speech_recognition as sr
from urllib.error import URLError
import time


BODY_URL = "http://localhost:6666"  # assuming it runs locally


class NaoStream:

    def __init__(self, audio_generator):
        self.audio_generator = audio_generator

    def read(self, size=-1):  # added size parameter, default -1
        try:
            return next(self.audio_generator)
        except StopIteration:
            return b''


class NaoAudioSource(sr.AudioSource):

    def __init__(self, server_url=BODY_URL):
        self.server_url = server_url
        self.stream = None
        self.is_listening = False
        self.CHUNK = 1365  # number of samples per audio chunk
        self.SAMPLE_RATE = 16000  # 16 kHz
        self.SAMPLE_WIDTH = 2  # each audio sample is 2 bytes

    def __enter__(self):  # this is called when using the "with" statement
        requests.post(f"{self.server_url}/start_listening")
        self.is_listening = True
        self.stream = NaoStream(self.audio_generator())  # wrap the generator
        return self  # return object (self) to be used in the with statement

    def audio_generator(self):  # generator function that continuously fetches audio chunks from the server as long as 'self.is_listening' is True

        sampling_frequency = 16000  # 16 kHz
        number_of_samples_per_chunk = 1365
        time_between_audio_chunks = number_of_samples_per_chunk / sampling_frequency  # in seconds
        corrected_time_between_audio_chunks = time_between_audio_chunks * 0.8

        while self.is_listening:
            response = requests.get(f"{self.server_url}/get_audio_chunk")
            yield response.content  # yield is used to return a value from a generator function, but unlike return, it doesn't terminate the function -> instead, it suspends the function and saves its state for later resumption
            current_buffer_length = requests.get(f"{self.server_url}/get_server_buffer_length").json()["length"]
            correcting_factor = 1.0 / (1.0 + np.exp(
                current_buffer_length - np.pi))  # if buffer becomes long, the time between audio chunks is decreased
            corrected_time_between_audio_chunks = time_between_audio_chunks * correcting_factor
            time.sleep(corrected_time_between_audio_chunks)  # wait for the next audio chunk to be available

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.is_listening = False
        requests.post(f"{self.server_url}/stop_listening")


def get_user_text():
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 1  # seconds of non-speaking audio before a phrase is considered complete
    recognizer.operation_timeout = 4  # increasing the timeout duration
    audio_data = None
    filename = "input.wav"

    sleep_time = 0.1  # in seconds

    while True:
        # record audio only if it hasn't been recorded yet
        if audio_data is None:
            with NaoAudioSource() as source:
                print("Recording...")
                start_time = time.time()
                audio_data = recognizer.listen(source, phrase_time_limit=10, timeout=None)
                with open(filename, "wb") as f:
                    f.write(audio_data.get_wav_data())
                print(f"Recording took {time.time() - start_time} seconds")

        # transcribe audio to text
        try:
            print("Transcribing...")
            start_time = time.time()
            text = recognizer.recognize_google(audio_data, language="it-IT")
            print(f"Transcribing took {time.time() - start_time} seconds")
            print("You said: " + text)
            return text
        except (sr.RequestError, URLError, ConnectionResetError) as e:
            print(f"Network error: {e}, retrying after a short delay...")
            time.sleep(sleep_time)  # adding a delay before retrying
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio, retrying...")
            audio_data = None  # reset audio_data to record again
        except TimeoutError as e:
            print(f"Operation timed out: {e}, retrying after a short delay...")
            audio_data = None  # reset audio_data to record again


def send_gpt_text_to_body(gpt_message):
    requests.post(f"{BODY_URL}/talk", json={"message": gpt_message})  # send the response to the body



running = True
while running:
    user_message = get_user_text()  # get the user's message


    send_gpt_text_to_body(user_message)
