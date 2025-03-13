# Choregraphe simplified export in Python.
from naoqi import ALProxy
names = list()
times = list()
keys = list()

names.append("HeadPitch")
times.append([0.1, 0.48, 1, 1.48, 2])
keys.append([-0.162646, -0.130432, 0.024502, 0.115008, 0.125746])

names.append("HeadYaw")
times.append([0.1, 0.48, 1, 1.48, 2])
keys.append([0.00149202, 0.07359, 0.162562, 0.21932, 0.320564])

names.append("LElbowRoll")
times.append([0.1, 0.48, 1, 1.48, 2])
keys.append([-0.432547, -0.757754, -1.017, -1.1612, -1.24863])

names.append("LElbowYaw")
times.append([0.1, 0.48, 1, 1.48, 2])
keys.append([-1.18429, -0.972599, -0.866752, -0.538476, -0.306842])

names.append("LHand")
times.append([0.1, 0.48, 1, 1.48, 2])
keys.append([0.2924, 0.2924, 0.2888, 0.2888, 0.2888])

names.append("LShoulderPitch")
times.append([0.1, 0.48, 1, 1.48, 2])
keys.append([1.42811, 0.998592, 0.613558, 0.254602, -0.0337899])

names.append("LShoulderRoll")
times.append([0.1, 0.48, 1, 1.48, 2])
keys.append([0.197844, -0.0123138, -0.0752079, -0.0291879, 0.0199001])

names.append("LWristYaw")
times.append([0.1, 0.48, 1, 1.48, 2])
keys.append([0.118076, -0.0506639, -0.142704, -0.145772, -0.0813439])

names.append("RElbowRoll")
times.append([0.1, 0.48, 1, 1.48, 2])
keys.append([0.412688, 0.563021, 0.796188, 1.17355, 1.45274])

names.append("RElbowYaw")
times.append([0.1, 0.48, 1, 1.48, 2])
keys.append([1.18267, 1.0845, 0.998592, 0.883542, 0.789968])

names.append("RHand")
times.append([0.1, 0.48, 1, 1.48, 2])
keys.append([0.2936, 0.2936, 0.2956, 0.2956, 0.2956])

names.append("RShoulderPitch")
times.append([0.1, 0.48, 1, 1.48, 2])
keys.append([1.4374, 1.15975, 0.949588, 0.93885, 0.93885])

names.append("RShoulderRoll")
times.append([0.1, 0.48, 1, 1.48, 2])
keys.append([-0.197927, 0.00302602, 0.0889301, -0.0368581, -0.098218])

names.append("RWristYaw")
times.append([0.1, 0.48, 1, 1.48, 2])
keys.append([0.0843279, -0.131966, -0.237812, -0.34059, -0.44797])

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
