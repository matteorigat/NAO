# Choregraphe simplified export in Python.
from naoqi import ALProxy
names = list()
times = list()
keys = list()

names.append("HeadPitch")
times.append([0.1, 1.08])
keys.append([-0.163066, 0.0873961])

names.append("HeadYaw")
times.append([0.1, 1.08])
keys.append([-0.00528999, -0.00310993])

names.append("LAnklePitch")
times.append([0.1, 1.08])
keys.append([0.0871523, 0.0873961])

names.append("LAnkleRoll")
times.append([0.1, 1.08])
keys.append([-0.107881, -0.10427])

names.append("LElbowRoll")
times.append([0.1, 0.52, 1.08])
keys.append([-0.417963, -0.801106, -1.46957])

names.append("LElbowYaw")
times.append([0.1, 0.52, 1.08])
keys.append([-1.19837, -0.596903, -0.421891])

names.append("LHand")
times.append([0.1, 1.08])
keys.append([0.295215, 0.186])

names.append("LHipPitch")
times.append([0.1, 1.08])
keys.append([0.12407, 0.12583])

names.append("LHipRoll")
times.append([0.1, 1.08])
keys.append([0.115978, 0.11049])

names.append("LHipYawPitch")
times.append([0.1, 1.08])
keys.append([-0.16949, -0.162562])

names.append("LKneePitch")
times.append([0.1, 1.08])
keys.append([-0.0920459, -0.099752])

names.append("LShoulderPitch")
times.append([0.1, 1.08])
keys.append([1.44214, 1.56157])

names.append("LShoulderRoll")
times.append([0.1, 0.52, 1.08])
keys.append([0.22343, 0.570866, 0.642281])

names.append("LWristYaw")
times.append([0.1, 1.08])
keys.append([0.0946459, 0.133416])

names.append("RAnklePitch")
times.append([0.1, 1.08])
keys.append([0.0871523, 0.0890141])

names.append("RAnkleRoll")
times.append([0.1, 1.08])
keys.append([0.107877, 0.11049])

names.append("RElbowRoll")
times.append([0.1, 0.52, 1.08])
keys.append([0.417961, 0.801106, 1.46957])

names.append("RElbowYaw")
times.append([0.1, 0.52, 1.08])
keys.append([1.20476, 0.596903, 0.230057])

names.append("RHand")
times.append([0.1, 1.08])
keys.append([0.296055, 0.1892])

names.append("RHipPitch")
times.append([0.1, 1.08])
keys.append([0.12407, 0.124212])

names.append("RHipRoll")
times.append([0.1, 1.08])
keys.append([-0.115972, -0.116542])

names.append("RHipYawPitch")
times.append([0.1, 1.08])
keys.append([-0.16949, -0.162562])

names.append("RKneePitch")
times.append([0.1, 1.08])
keys.append([-0.0920459, -0.091998])

names.append("RShoulderPitch")
times.append([0.1, 1.08])
keys.append([1.43703, 1.47115])

names.append("RShoulderRoll")
times.append([0.1, 0.52, 1.08])
keys.append([-0.22343, -0.570866, -0.642281])

names.append("RWristYaw")
times.append([0.1, 1.08])
keys.append([0.0964521, -0.2102])


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
