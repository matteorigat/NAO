# Choregraphe simplified export in Python.
from naoqi import ALProxy
names = list()
times = list()
keys = list()

names.append("LElbowRoll")
times.append([1.24])
keys.append([-1.53764])

names.append("LElbowYaw")
times.append([1.24])
keys.append([-2.04727])

names.append("LHand")
times.append([1.24])
keys.append([0.93])

names.append("LShoulderPitch")
times.append([1.24])
keys.append([1.33692])

names.append("LWristYaw")
times.append([1.24])
keys.append([-0.869174])

names.append("RElbowRoll")
times.append([1.24])
keys.append([1.53764])

names.append("RElbowYaw")
times.append([1.24])
keys.append([2.04727])

names.append("RHand")
times.append([1.24])
keys.append([0.93])

names.append("RShoulderPitch")
times.append([1.24])
keys.append([1.33692])

names.append("RWristYaw")
times.append([1.24])
keys.append([0.869174])

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
