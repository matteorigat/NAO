# Choregraphe simplified export in Python.
from naoqi import ALProxy
names = list()
times = list()
keys = list()

names.append("HeadPitch")
times.append([0.1, 0.56, 0.96, 1.32, 1.72])
keys.append([-0.144238, -0.0567998, 0.0444441, 0.220854, 0.220854])

names.append("HeadYaw")
times.append([0.1, 0.56, 0.96, 1.32, 1.72])
keys.append([-4.19617e-05, -0.01845, -0.0813439, -0.105888, -0.362067])

names.append("LElbowRoll")
times.append([0.1, 0.56, 0.96, 1.32, 1.72])
keys.append([-0.432547, -0.757754, -1.0262, -1.22716, -1.2379])

names.append("LElbowYaw")
times.append([0.1, 0.56, 0.96, 1.32, 1.72])
keys.append([-1.18429, -0.972599, -0.89283, -0.905102, -0.83914])

names.append("LHand")
times.append([0.1, 0.56, 0.96, 1.32, 1.72])
keys.append([0.2924, 0.2924, 0.2924, 0.2924, 0.2924])

names.append("LShoulderPitch")
times.append([0.1, 0.56, 0.96, 1.32, 1.72])
keys.append([1.42811, 0.998592, 0.59515, 0.0705221, -0.251617])

names.append("LShoulderRoll")
times.append([0.1, 0.56, 0.96, 1.32, 1.72])
keys.append([0.197844, -0.0123138, -0.093616, -0.101286, -0.0690719])

names.append("LWristYaw")
times.append([0.1, 0.56, 0.96, 1.32, 1.72])
keys.append([0.118076, -0.0506639, -0.167248, -0.234743, -0.291501])

names.append("RElbowRoll")
times.append([0.1, 0.56, 0.96, 1.32, 1.72])
keys.append([0.412688, 0.563021, 0.813062, 1.43433, 1.5049])

names.append("RElbowYaw")
times.append([0.1, 0.56, 0.96, 1.32, 1.72])
keys.append([1.18267, 1.0845, 1.017, 0.941834, 0.862065])

names.append("RHand")
times.append([0.1, 0.56, 0.96, 1.32, 1.72])
keys.append([0.2936, 0.2936, 0.2936, 0.2936, 0.2936])

names.append("RShoulderPitch")
times.append([0.1, 0.56, 0.96, 1.32, 1.72])
keys.append([1.4374, 1.15975, 0.89283, 0.737896, 0.428028])

names.append("RShoulderRoll")
times.append([0.1, 0.56, 0.96, 1.32, 1.72])
keys.append([-0.197927, 0.00302602, 0.116542, 0.176367, 0.214717])

names.append("RWristYaw")
times.append([0.1, 0.56, 0.96, 1.32, 1.72])
keys.append([0.0843279, -0.131966, -0.214803, -0.214803, -0.214803])

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
