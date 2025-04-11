# Choregraphe simplified export in Python.
from naoqi import ALProxy
names = list()
times = list()
keys = list()

names.append("LElbowRoll")
times.append([0.76])
keys.append([-0.0523599])

names.append("LElbowYaw")
times.append([0.76])
keys.append([-1.24442])

names.append("LShoulderRoll")
times.append([0.76, 1.6])
keys.append([0.532325, 0.734784])

names.append("RElbowRoll")
times.append([0.76])
keys.append([0.0349066])

names.append("RElbowYaw")
times.append([0.76])
keys.append([1.24442])

names.append("RShoulderPitch")
times.append([0.76, 1.6])
keys.append([0.0139626, -1.01229])

names.append("RShoulderRoll")
times.append([0.76, 1.6])
keys.append([-0.637045, -0.692896])

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
