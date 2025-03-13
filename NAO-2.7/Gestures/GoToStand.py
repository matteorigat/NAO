# Choregraphe simplified export in Python.
from naoqi import ALProxy
names = list()
times = list()
keys = list()

names.append("HeadPitch")
times.append([2.44])
keys.append([-0.161945])

names.append("HeadYaw")
times.append([2.44])
keys.append([0.00545863])

names.append("LAnklePitch")
times.append([2.44])
keys.append([0.0774271])

names.append("LAnkleRoll")
times.append([2.44])
keys.append([-0.108831])

names.append("LElbowRoll")
times.append([2.44])
keys.append([-0.421299])

names.append("LElbowYaw")
times.append([2.44])
keys.append([-1.19424])

names.append("LHand")
times.append([2.44])
keys.append([0.299388])

names.append("LHipPitch")
times.append([2.44])
keys.append([0.121381])

names.append("LHipRoll")
times.append([2.44])
keys.append([0.116999])

names.append("LHipYawPitch")
times.append([2.44])
keys.append([-0.161954])

names.append("LKneePitch")
times.append([2.44])
keys.append([-0.0921395])

names.append("LShoulderPitch")
times.append([2.44])
keys.append([1.44137])

names.append("LShoulderRoll")
times.append([2.44])
keys.append([0.220753])

names.append("LWristYaw")
times.append([2.44])
keys.append([0.0932922])

names.append("RAnklePitch")
times.append([2.44])
keys.append([0.0774271])

names.append("RAnkleRoll")
times.append([2.44])
keys.append([0.108827])

names.append("RElbowRoll")
times.append([2.44])
keys.append([0.421299])

names.append("RElbowYaw")
times.append([2.44])
keys.append([1.19424])

names.append("RHand")
times.append([2.44])
keys.append([0.299388])

names.append("RHipPitch")
times.append([2.44])
keys.append([0.121382])

names.append("RHipRoll")
times.append([2.44])
keys.append([-0.116993])

names.append("RHipYawPitch")
times.append([2.44])
keys.append([-0.161954])

names.append("RKneePitch")
times.append([2.44])
keys.append([-0.0921395])

names.append("RShoulderPitch")
times.append([2.44])
keys.append([1.44137])

names.append("RShoulderRoll")
times.append([2.44])
keys.append([-0.220753])

names.append("RWristYaw")
times.append([2.44])
keys.append([0.0932922])

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
