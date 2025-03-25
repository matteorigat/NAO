# Choregraphe simplified export in Python.
from naoqi import ALProxy
names = list()
times = list()
keys = list()

names.append("HeadPitch")
times.append([0])
keys.append([-0.17])

names.append("HeadYaw")
times.append([0])
keys.append([0])

names.append("LAnklePitch")
times.append([0])
keys.append([0.0874194])

names.append("LAnkleRoll")
times.append([0])
keys.append([-0.110793])

names.append("LElbowRoll")
times.append([0, 1.24])
keys.append([-0.418595, -1.53764])

names.append("LElbowYaw")
times.append([0, 1.24])
keys.append([-1.2059, -2.04727])

names.append("LHand")
times.append([0, 1.24])
keys.append([0.3, 0.93])

names.append("LHipPitch")
times.append([0])
keys.append([0.127419])

names.append("LHipRoll")
times.append([0])
keys.append([0.119108])

names.append("LHipYawPitch")
times.append([0])
keys.append([-0.17001])

names.append("LKneePitch")
times.append([0])
keys.append([-0.0923279])

names.append("LShoulderPitch")
times.append([0, 1.24])
keys.append([1.4375, 1.33692])

names.append("LShoulderRoll")
times.append([0])
keys.append([0.22256])

names.append("LWristYaw")
times.append([0, 1.24])
keys.append([0.0975551, -0.869174])

names.append("RAnklePitch")
times.append([0])
keys.append([0.0874193])

names.append("RAnkleRoll")
times.append([0])
keys.append([0.110789])

names.append("RElbowRoll")
times.append([0, 1.24])
keys.append([0.418595, 1.53764])

names.append("RElbowYaw")
times.append([0, 1.24])
keys.append([1.2059, 2.04727])

names.append("RHand")
times.append([0, 1.24])
keys.append([0.3, 0.93])

names.append("RHipPitch")
times.append([0])
keys.append([0.127419])

names.append("RHipRoll")
times.append([0])
keys.append([-0.119102])

names.append("RHipYawPitch")
times.append([0])
keys.append([-0.17001])

names.append("RKneePitch")
times.append([0])
keys.append([-0.0923279])

names.append("RShoulderPitch")
times.append([0, 1.24])
keys.append([1.4375, 1.33692])

names.append("RShoulderRoll")
times.append([0])
keys.append([-0.22256])

names.append("RWristYaw")
times.append([0, 1.24])
keys.append([0.100506, 0.869174])

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
