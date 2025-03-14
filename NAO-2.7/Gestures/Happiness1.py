# Choregraphe simplified export in Python.
from naoqi import ALProxy
names = list()
times = list()
keys = list()

names.append("HeadPitch")
times.append([0, 0.84, 1.56])
keys.append([-0.17329, -0.164746, -0.436332])

names.append("HeadYaw")
times.append([0, 0.84])
keys.append([-0.00400687, 0])

names.append("LAnklePitch")
times.append([0, 0.84])
keys.append([0.0871523, 0.0815694])

names.append("LAnkleRoll")
times.append([0, 0.84])
keys.append([-0.107881, -0.103379])

names.append("LElbowRoll")
times.append([0, 0.84])
keys.append([-0.421949, -0.403243])

names.append("LElbowYaw")
times.append([0, 0.84])
keys.append([-1.20049, -1.19119])

names.append("LHand")
times.append([0, 0.84, 1.56])
keys.append([0.290728, 0.290728, 1])

names.append("LHipPitch")
times.append([0, 0.84])
keys.append([0.12407, 0.123481])

names.append("LHipRoll")
times.append([0, 0.84])
keys.append([0.115978, 0.118153])

names.append("LHipYawPitch")
times.append([0, 0.84])
keys.append([-0.16949, -0.164755])

names.append("LKneePitch")
times.append([0, 0.84])
keys.append([-0.0920459, -0.0923279])

names.append("LShoulderPitch")
times.append([0, 0.84, 1.56])
keys.append([1.43935, 0.308037, -0.787143])

names.append("LShoulderRoll")
times.append([0, 0.84, 1.56])
keys.append([0.215447, 0.383972, 0.350811])

names.append("LWristYaw")
times.append([0, 0.84])
keys.append([0.108394, 0.168904])

names.append("RAnklePitch")
times.append([0, 0.84])
keys.append([0.0871523, 0.0815694])

names.append("RAnkleRoll")
times.append([0, 0.84])
keys.append([0.107877, 0.103375])

names.append("RElbowRoll")
times.append([0, 0.84])
keys.append([0.421949, 0.403243])

names.append("RElbowYaw")
times.append([0, 0.84])
keys.append([1.20049, 1.19119])

names.append("RHand")
times.append([0, 0.84, 1.56])
keys.append([0.290728, 0.290728, 1])

names.append("RHipPitch")
times.append([0, 0.84])
keys.append([0.12407, 0.123481])

names.append("RHipRoll")
times.append([0, 0.84])
keys.append([-0.115972, -0.118147])

names.append("RHipYawPitch")
times.append([0, 0.84])
keys.append([-0.16949, -0.164755])

names.append("RKneePitch")
times.append([0, 0.84])
keys.append([-0.0920459, -0.0923279])

names.append("RShoulderPitch")
times.append([0, 0.84, 1.56])
keys.append([1.43935, 0.308037, -0.787143])

names.append("RShoulderRoll")
times.append([0, 0.84, 1.56])
keys.append([-0.215447, -0.383972, -0.350811])

names.append("RWristYaw")
times.append([0, 0.84])
keys.append([0.0985636, -0.165563])

def execute_gesture(IP, PORT, reverse=False):
    """Esegue il gesto sulla robot NAO"""
    try:
        # Prepara i dizionari per memorizzare i tempi e i keyframe invertiti
        reversed_times = []
        reversed_keys = []

        if reverse:
            total_time = 0
            for i in range(len(times)):
                if times[i][-1] > total_time:
                    total_time = times[i][-1]
                    
            # Calcoliamo i nuovi tempi invertiti e i keyframe corrispondenti
            for i, name in enumerate(names):
                # Invertiamo i tempi come richiesto (total_time - time)
                reversed_times_for_joint = [total_time - t for t in times[i]]
                reversed_times_for_joint.sort()  # Ordinare i tempi in ordine crescente

                # Invertiamo i keyframe mantenendo la corrispondenza con i nuovi tempi
                reversed_keys_for_joint = list(reversed(keys[i]))  # Invertiamo i keyframe

                reversed_times.append(reversed_times_for_joint)
                reversed_keys.append(reversed_keys_for_joint)
        else:
            reversed_times = times
            reversed_keys = keys

        for i in range(len(reversed_times)):
            if reversed_times[i][0] <= 0:
                reversed_times[i][0] = 0.1


        # Esegui il gesto sul robot NAO
        motion = ALProxy("ALMotion", IP, PORT)
        motion.angleInterpolation(names, reversed_keys, reversed_times, True)

    except BaseException as err:
        print(err)
