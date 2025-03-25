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
