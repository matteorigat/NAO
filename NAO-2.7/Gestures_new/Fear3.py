# Choregraphe simplified export in Python.
from naoqi import ALProxy
names = list()
times = list()
keys = list()

names.append("HeadPitch")
times.append([0, 0.56, 0.96, 1.32, 1.68, 1.96, 2.36])
keys.append([-0.144238, -0.0567998, 0.0444441, 0.220854, 0.220854, 0.254602, 0.26534])

names.append("HeadYaw")
times.append([0, 0.56, 0.96, 1.32, 1.68, 1.96, 2.36])
keys.append([-4.19617e-05, -0.01845, -0.0813439, -0.105888, -0.362067, -0.477116, -0.604438])

names.append("LElbowRoll")
times.append([0, 0.56, 0.96, 1.32, 1.68, 1.96, 2.36])
keys.append([-0.432547, -0.757754, -1.0262, -1.22716, -1.2379, -1.13972, -0.665714])

names.append("LElbowYaw")
times.append([0, 0.56, 0.96, 1.32, 1.68, 1.96, 2.36])
keys.append([-1.18429, -0.972599, -0.89283, -0.905102, -0.83914, -0.833004, -0.80079])

names.append("LHand")
times.append([0, 0.56, 0.96, 1.32, 1.68, 1.96, 2.36])
keys.append([0.2924, 0.2924, 0.2924, 0.2924, 0.2924, 0.68, 1])

names.append("LShoulderPitch")
times.append([0, 0.56, 0.96, 1.32, 1.68, 1.96, 2.36])
keys.append([1.42811, 0.998592, 0.59515, 0.0705221, -0.251617, -0.0521979, 0.167164])

names.append("LShoulderRoll")
times.append([0, 0.56, 0.96, 1.32, 1.68, 1.96, 2.36])
keys.append([0.197844, -0.0123138, -0.093616, -0.101286, -0.0690719, 0.369652, 0.650374])

names.append("LWristYaw")
times.append([0, 0.56, 0.96, 1.32, 1.68, 1.96, 2.36])
keys.append([0.118076, -0.0506639, -0.167248, -0.234743, -0.291501, -0.268492, 1.25477])

names.append("RElbowRoll")
times.append([0, 0.56, 0.96, 1.32, 1.68, 1.96, 2.36])
keys.append([0.412688, 0.563021, 0.813062, 1.43433, 1.5049, 1.45121, 1.44047])

names.append("RElbowYaw")
times.append([0, 0.56, 0.96, 1.32, 1.68, 1.96, 2.36])
keys.append([1.18267, 1.0845, 1.017, 0.941834, 0.862065, 0.865134, 0.866668])

names.append("RHand")
times.append([0, 0.56, 0.96, 1.32, 1.68, 1.96, 2.36])
keys.append([0.2936, 0.2936, 0.2936, 0.2936, 0.2936, 0.2956, 0.2956])

names.append("RShoulderPitch")
times.append([0, 0.56, 0.96, 1.32, 1.68, 1.96, 2.36])
keys.append([1.4374, 1.15975, 0.89283, 0.737896, 0.428028, 0.521602, 0.549214])

names.append("RShoulderRoll")
times.append([0, 0.56, 0.96, 1.32, 1.68, 1.96, 2.36])
keys.append([-0.197927, 0.00302602, 0.116542, 0.176367, 0.214717, 0.147222, 0.13495])

names.append("RWristYaw")
times.append([0, 0.56, 0.96, 1.32, 1.68, 1.96, 2.36])
keys.append([0.0843279, -0.131966, -0.214803, -0.214803, -0.214803, -0.196394, -0.188724])

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
