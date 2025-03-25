# Choregraphe simplified export in Python.
from naoqi import ALProxy
names = list()
times = list()
keys = list()

names.append("HeadPitch")
times.append([0, 1.52])
keys.append([0.265341, -0.144238])

names.append("HeadYaw")
times.append([0, 1.52])
keys.append([-0.604439, -4.19617e-05])

names.append("LElbowRoll")
times.append([0, 1.52])
keys.append([-0.665714, -0.432547])

names.append("LElbowYaw")
times.append([0, 1.52])
keys.append([-0.80079, -1.18429])

names.append("LHand")
times.append([0, 1.52])
keys.append([1, 0.2924])

names.append("LShoulderPitch")
times.append([0, 1.52])
keys.append([0.167164, 1.42811])

names.append("LShoulderRoll")
times.append([0, 1.52])
keys.append([0.650374, 0.197844])

names.append("LWristYaw")
times.append([0, 1.52])
keys.append([1.25477, 0.118076])

names.append("RElbowRoll")
times.append([0, 1.52])
keys.append([1.44047, 0.412688])

names.append("RElbowYaw")
times.append([0, 1.52])
keys.append([0.866668, 1.18267])

names.append("RHand")
times.append([0, 1.52])
keys.append([0.2956, 0.2936])

names.append("RShoulderPitch")
times.append([0, 1.52])
keys.append([0.549213, 1.4374])

names.append("RShoulderRoll")
times.append([0, 1.52])
keys.append([0.13495, -0.197927])

names.append("RWristYaw")
times.append([0, 1.52])
keys.append([-0.188724, 0.0843279])

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