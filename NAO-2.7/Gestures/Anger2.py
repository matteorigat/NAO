# Choregraphe simplified export in Python.
from naoqi import ALProxy
names = list()
times = list()
keys = list()

names.append("HeadPitch")
times.append([0.1, 0.96])
keys.append([-0.166041, 0.199378])

names.append("HeadYaw")
times.append([0.1, 0.96])
keys.append([-0.00400687, -0.00310993])

names.append("LAnklePitch")
times.append([0.1, 0.96])
keys.append([0.0871523, 0.0873961])

names.append("LAnkleRoll")
times.append([0.1, 0.96])
keys.append([-0.107881, -0.10427])

names.append("LElbowRoll")
times.append([0.1, 0.96])
keys.append([-0.421029, -0.0551819])

names.append("LElbowYaw")
times.append([0.1, 0.96])
keys.append([-1.19766, -1.47268])

names.append("LHand")
times.append([0.1, 0.96])
keys.append([0.293013, 0.0164])

names.append("LHipPitch")
times.append([0.1, 0.96])
keys.append([0.12407, 0.12583])

names.append("LHipRoll")
times.append([0.1, 0.96])
keys.append([0.115978, 0.11049])

names.append("LHipYawPitch")
times.append([0.1, 0.96])
keys.append([-0.16949, -0.162562])

names.append("LKneePitch")
times.append([0.1, 0.96])
keys.append([-0.0920459, -0.099752])

names.append("LShoulderPitch")
times.append([0.1, 0.96])
keys.append([1.45202, 1.42811])

names.append("LShoulderRoll")
times.append([0.1, 0.96])
keys.append([0.225233, 0.312894])

names.append("LWristYaw")
times.append([0.1, 0.96])
keys.append([0.0903604, 0.0996681])

names.append("RAnklePitch")
times.append([0.1, 0.96])
keys.append([0.0871523, 0.0890141])

names.append("RAnkleRoll")
times.append([0.1, 0.96])
keys.append([0.107877, 0.11049])

names.append("RElbowRoll")
times.append([0.1, 0.96])
keys.append([0.421029, 0.0552659])

names.append("RElbowYaw")
times.append([0.1, 0.96])
keys.append([1.19766, 1.4726])

names.append("RHand")
times.append([0.1, 0.96])
keys.append([0.293013, 0.0136])

names.append("RHipPitch")
times.append([0.1, 0.96])
keys.append([0.12407, 0.124212])

names.append("RHipRoll")
times.append([0.1, 0.96])
keys.append([-0.115972, -0.116542])

names.append("RHipYawPitch")
times.append([0.1, 0.96])
keys.append([-0.16949, -0.162562])

names.append("RKneePitch")
times.append([0.1, 0.96])
keys.append([-0.0920459, -0.091998])

names.append("RShoulderPitch")
times.append([0.1, 0.96])
keys.append([1.45203, 1.44354])

names.append("RShoulderRoll")
times.append([0.1, 0.96])
keys.append([-0.225233, -0.31758])

names.append("RWristYaw")
times.append([0.1, 0.96])
keys.append([0.0903604, 0.076658])

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
