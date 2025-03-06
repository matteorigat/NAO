# Choregraphe simplified export in Python.
from naoqi import ALProxy


names = list()
times = list()
keys = list()

names.append("HeadPitch")
times.append([0.5, 1])
keys.append([0, 0])

names.append("HeadYaw")
times.append([0.5, 1])
keys.append([0, 0])



names.append("LShoulderPitch")
times.append([0.5, 1])
keys.append([0, 1])

names.append("LShoulderRoll")
times.append([0.5, 1])
keys.append([0, 1])

names.append("LElbowYaw")
times.append([0.5, 1])
keys.append([0, 0])

names.append("LElbowRoll")
times.append([0.5, 1])
keys.append([0, 0])

names.append("LWristYaw")
times.append([0.5, 1])
keys.append([0, 0])

names.append("LHand")
times.append([0.5, 1])
keys.append([0, 1])



names.append("RShoulderPitch")
times.append([0.5, 1])
keys.append([0, 0])

names.append("RShoulderRoll")
times.append([0.5, 1])
keys.append([0, 0])

names.append("RElbowYaw")
times.append([0.5, 1])
keys.append([0, 0])

names.append("RElbowRoll")
times.append([0.5, 1])
keys.append([0, 0])

names.append("RWristYaw")
times.append([0.5, 1])
keys.append([0, 0])

names.append("RHand")
times.append([0.5, 1])
keys.append([0, 1])



###################################################
###################################################
###################################################


names.append("LHipPitch")
times.append([0.5, 1])
keys.append([0, 0])

names.append("LHipRoll")
times.append([0.5, 1])
keys.append([0, 0])

names.append("LHipYawPitch")
times.append([0.5, 1])
keys.append([0, 0])

names.append("LAnklePitch")
times.append([0.5, 1])
keys.append([0, 0])

names.append("LAnkleRoll")
times.append([0.5, 1])
keys.append([0, 0])

names.append("LKneePitch")
times.append([0.5, 1])
keys.append([0, 0])

names.append("RAnklePitch")
times.append([0.5, 1])
keys.append([0, 0])

names.append("RAnkleRoll")
times.append([0.5, 1])
keys.append([0, 0])

names.append("RHipPitch")
times.append([0.5, 1])
keys.append([0, 0])

names.append("RHipRoll")
times.append([0.5, 1])
keys.append([0, 0])

names.append("RHipYawPitch")
times.append([0.5, 1])
keys.append([0, 0])

names.append("RKneePitch")
times.append([0.5, 1])
keys.append([0, 0])




try:
  # uncomment the following line and modify the IP if you use this script outside Choregraphe.
  motion = ALProxy("ALMotion", "127.0.0.1", 9559)
  motion.angleInterpolation(names, keys, times, True)
except BaseException, err:
  print err
