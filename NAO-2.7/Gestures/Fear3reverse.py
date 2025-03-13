# Choregraphe simplified export in Python.
from naoqi import ALProxy
names = list()
times = list()
keys = list()

names.append("HeadPitch")
times.append([0.1, 1.52])
keys.append([0.265341, -0.144238])

names.append("HeadYaw")
times.append([0.1, 1.52])
keys.append([-0.604439, -4.19617e-05])

names.append("LElbowRoll")
times.append([0.1, 1.52])
keys.append([-0.665714, -0.432547])

names.append("LElbowYaw")
times.append([0.1, 1.52])
keys.append([-0.80079, -1.18429])

names.append("LHand")
times.append([0.1, 1.52])
keys.append([1, 0.2924])

names.append("LShoulderPitch")
times.append([0.1, 1.52])
keys.append([0.167164, 1.42811])

names.append("LShoulderRoll")
times.append([0.1, 1.52])
keys.append([0.650374, 0.197844])

names.append("LWristYaw")
times.append([0.1, 1.52])
keys.append([1.25477, 0.118076])

names.append("RElbowRoll")
times.append([0.1, 1.52])
keys.append([1.44047, 0.412688])

names.append("RElbowYaw")
times.append([0.1, 1.52])
keys.append([0.866668, 1.18267])

names.append("RHand")
times.append([0.1, 1.52])
keys.append([0.2956, 0.2936])

names.append("RShoulderPitch")
times.append([0.1, 1.52])
keys.append([0.549213, 1.4374])

names.append("RShoulderRoll")
times.append([0.1, 1.52])
keys.append([0.13495, -0.197927])

names.append("RWristYaw")
times.append([0.1, 1.52])
keys.append([-0.188724, 0.0843279])

def execute_gesture(IP, PORT, reverse=False):
  """Esegue il gesto sulla robot NAO"""
  try:
      # Calcoliamo il tempo totale (l'ultimo tempo nella lista dei tempi)
      total_time = times[0][-1]  # Consideriamo l'ultimo valore di tempo per il calcolo

      if reverse:
          reversed_times = []
          reversed_keys = []

          # Calcoliamo i nuovi tempi inversi e i keyframe corrispondenti
          for i, name in enumerate(names):
              reversed_times_for_joint = [total_time - t for t in times[i]]  # Invertiamo i tempi
              reversed_keys_for_joint = list(reversed(keys[i]))  # Invertiamo i keyframe
              reversed_times.append(reversed_times_for_joint)
              reversed_keys.append(reversed_keys_for_joint)
      else:
          reversed_times = times
          reversed_keys = keys

      motion = ALProxy("ALMotion", IP, PORT)
      motion.angleInterpolation(names, reversed_keys, reversed_times, True)
  except BaseException as err:
      print(err)

# Permette di eseguire lo script direttamente
if __name__ == "__main__":
  NAO_IP = "127.0.0.1"
  NAO_PORT = 9559
  execute_gesture(NAO_IP, NAO_PORT)