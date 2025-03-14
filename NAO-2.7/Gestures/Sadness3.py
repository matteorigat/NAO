# Choregraphe simplified export in Python.
from naoqi import ALProxy
names = list()
times = list()
keys = list()

names.append("HeadPitch")
times.append([0, 0.44, 2.32, 2.76, 3.12, 3.44, 3.76, 4.12, 4.48, 4.88, 5.2, 5.48])
keys.append([-0.144238, -0.07214, 0.285283, 0.265341, 0.265341, 0.265341, 0.265341, 0.265341, 0.265341, 0.265341, 0.265341, 0.265341])

names.append("HeadYaw")
times.append([0, 0.44, 2.32, 2.76, 3.12, 3.44, 3.76, 4.12, 4.48, 4.88, 5.2, 5.48])
keys.append([-4.19617e-05, -0.0813439, -0.618244, -0.958186, -0.532325, -0.312978, -0.532325, -0.958186, -0.532325, -0.312978, -0.532325, -0.958186])

names.append("LElbowRoll")
times.append([0, 0.44, 1.2, 1.68, 2.32, 2.76, 3.12, 3.44, 3.76, 4.12, 4.48, 4.88, 5.2, 5.48])
keys.append([-0.424876, -0.424876, -0.424876, -0.424876, -0.424876, -0.424876, -0.424876, -0.424876, -0.424876, -0.424876, -0.424876, -0.424876, -0.424876, -0.424876])

names.append("LElbowYaw")
times.append([0, 0.44, 1.2, 1.68, 2.32, 2.76, 3.12, 3.44, 3.76, 4.12, 4.48, 4.88, 5.2, 5.48])
keys.append([-1.18582, -1.18582, -1.18582, -1.18582, -1.18582, -1.18582, -1.18582, -1.18582, -1.18582, -1.18582, -1.18582, -1.18582, -1.18582, -1.18582])

names.append("LHand")
times.append([0, 0.44, 1.2, 1.68, 2.32, 2.76, 3.12, 3.44, 3.76, 4.12, 4.48, 4.88, 5.2, 5.48])
keys.append([0.2888, 0.2888, 0.2888, 0.2888, 0.2888, 0.2888, 0.2888, 0.2888, 0.2888, 0.2888, 0.2888, 0.2888, 0.2888, 0.2888])

names.append("LShoulderPitch")
times.append([0, 0.44, 1.2, 1.68, 2.32, 2.76, 3.12, 3.44, 3.76, 4.12, 4.48, 4.88, 5.2, 5.48])
keys.append([1.44499, 1.44499, 1.44499, 1.44499, 1.44499, 1.44499, 1.44499, 1.44499, 1.44499, 1.44499, 1.44499, 1.44499, 1.44499, 1.44499])

names.append("LShoulderRoll")
times.append([0, 0.44, 1.2, 1.68, 2.32, 2.76, 3.12, 3.44, 3.76, 4.12, 4.48, 4.88, 5.2, 5.48])
keys.append([0.197844, 0.214717, 0.213185, 0.213185, 0.211651, 0.211651, 0.211651, 0.211651, 0.211651, 0.211651, 0.211651, 0.211651, 0.211651, 0.211651])

names.append("LWristYaw")
times.append([0, 0.44, 1.2, 1.68, 2.32, 2.76, 3.12, 3.44, 3.76, 4.12, 4.48, 4.88, 5.2, 5.48])
keys.append([0.0797259, 0.0797259, 0.0797259, 0.0797259, 0.0797259, 0.0797259, 0.0797259, 0.0797259, 0.0797259, 0.0797259, 0.0797259, 0.0797259, 0.0797259, 0.0797259])

names.append("RElbowRoll")
times.append([0, 0.44, 1.2, 1.68, 2.32, 2.76, 3.12, 3.44, 3.76, 4.12, 4.48, 4.88, 5.2, 5.48])
keys.append([0.414222, 0.60904, 1.23645, 1.46808, 1.52944, 1.52944, 1.52944, 1.52944, 1.52944, 1.52944, 1.52944, 1.52944, 1.52944, 1.52944])

names.append("RElbowYaw")
times.append([0, 0.44, 1.2, 1.68, 2.32, 2.76, 3.12, 3.44, 3.76, 4.12, 4.48, 4.88, 5.2, 5.48])
keys.append([1.18421, 0.223922, -0.224006, -0.245482, -0.15651, -0.15651, -0.15651, -0.15651, -0.15651, -0.15651, -0.15651, -0.15651, -0.15651, -0.15651])

names.append("RHand")
times.append([0, 0.44, 1.2, 1.68, 2.32, 2.76, 3.12, 3.44, 3.76, 4.12, 4.48, 4.88, 5.2, 5.48])
keys.append([0.2956, 0.2956, 0.2956, 0.2956, 0.2956, 0.2956, 0.2956, 0.2956, 0.2956, 0.2956, 0.2956, 0.2956, 0.2956, 0.2956])

names.append("RShoulderPitch")
times.append([0, 0.44, 1.2, 1.68, 2.32, 2.76, 3.12, 3.44, 3.76, 4.12, 4.48, 4.88, 5.2, 5.48])
keys.append([1.45121, 1.13367, 0.633584, 0.0583338, -0.487771, -0.487771, -0.487771, -0.487771, -0.487771, -0.487771, -0.487771, -0.487771, -0.487771, -0.487771])

names.append("RShoulderRoll")
times.append([0, 0.44, 1.2, 1.68, 2.32, 2.76, 3.12, 3.44, 3.76, 4.12, 4.48, 4.88, 5.2, 5.48])
keys.append([-0.200996, -0.242414, -0.372804, -0.385075, -0.369736, -0.369736, -0.369736, -0.369736, -0.369736, -0.369736, -0.369736, -0.369736, -0.369736, -0.369736])

names.append("RWristYaw")
times.append([0, 0.44, 1.2, 1.68, 2.32, 2.76, 3.12, 3.44, 3.76, 4.12, 4.48, 4.88, 5.2, 5.48])
keys.append([0.0797259, 0.569072, 0.76389, 0.76389, 0.799172, 0.799172, 0.799172, 0.799172, 0.799172, 0.799172, 0.799172, 0.799172, 0.799172, 0.799172])

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
