# Choregraphe simplified export in Python.
from naoqi import ALProxy
names = list()
times = list()
keys = list()

names.append("HeadPitch")
times.append([0, 0.56, 0.96, 1.32, 1.72])
keys.append([0.293215, -0.0567998, 0.0444441, 0.21932, 0.28068])

names.append("HeadYaw")
times.append([0, 0.56, 0.96, 1.32, 1.72])
keys.append([-4.19617e-05, -0.01845, -0.0813439, -0.0598679, -0.046062])

names.append("LElbowRoll")
times.append([0, 0.56, 0.96, 1.32, 1.72])
keys.append([-0.432547, -0.757754, -1.01393, -1.30693, -1.53396])

names.append("LElbowYaw")
times.append([0, 0.56, 0.96, 1.32, 1.72])
keys.append([-1.18429, -0.972599, -0.902033, -0.872888, -0.865217])

names.append("LHand")
times.append([0, 0.56, 0.96, 1.32, 1.72])
keys.append([0.2924, 0.2924, 0.2888, 0.2888, 0.2888])

names.append("LShoulderPitch")
times.append([0, 0.56, 0.96, 1.32, 1.72])
keys.append([1.42811, 0.998592, 0.641169, 0.510779, 0.408002])

names.append("LShoulderRoll")
times.append([0, 0.56, 0.96, 1.32, 1.72])
keys.append([0.197844, -0.0123138, 0.021434, -0.0138481, -0.0429941])

names.append("LWristYaw")
times.append([0, 0.56, 0.96, 1.32, 1.72])
keys.append([0.118076, -0.0506639, -0.177985, -0.509331, -0.731761])

names.append("RElbowRoll")
times.append([0, 0.56, 0.96, 1.32, 1.72])
keys.append([0.412688, 0.563021, 1.2119, 1.43587, 1.53558])

names.append("RElbowYaw")
times.append([0, 0.56, 0.96, 1.32, 1.72])
keys.append([1.18267, 1.0845, 0.831386, 0.770025, 0.780764])

names.append("RHand")
times.append([0, 0.56, 0.96, 1.32, 1.72])
keys.append([0.2936, 0.2936, 0.2956, 0.2956, 0.2956])

names.append("RShoulderPitch")
times.append([0, 0.56, 0.96, 1.32, 1.72])
keys.append([1.4374, 1.15975, 0.690342, 0.47865, 0.329852])

names.append("RShoulderRoll")
times.append([0, 0.56, 0.96, 1.32, 1.72])
keys.append([-0.197927, 0.00302602, -0.219404, -0.197927, -0.185656])

names.append("RWristYaw")
times.append([0, 0.56, 0.96, 1.32, 1.72])
keys.append([0.0843279, -0.131966, 0.328234, 0.728609, 0.921892])

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
