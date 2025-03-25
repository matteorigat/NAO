# Choregraphe simplified export in Python.
from naoqi import ALProxy
names = list()
times = list()
keys = list()

names.append("HeadPitch")
times.append([1.08])
keys.append([0.0873961])

names.append("HeadYaw")
times.append([1.08])
keys.append([-0.00310993])

names.append("LAnklePitch")
times.append([1.08])
keys.append([0.0873961])

names.append("LAnkleRoll")
times.append([1.08])
keys.append([-0.10427])

names.append("LElbowRoll")
times.append([0.52, 1.08])
keys.append([-0.801106, -1.46957])

names.append("LElbowYaw")
times.append([0.52, 1.08])
keys.append([-0.596903, -0.421891])

names.append("LHand")
times.append([1.08])
keys.append([0.186])

names.append("LHipPitch")
times.append([1.08])
keys.append([0.12583])

names.append("LHipRoll")
times.append([1.08])
keys.append([0.11049])

names.append("LHipYawPitch")
times.append([1.08])
keys.append([-0.162562])

names.append("LKneePitch")
times.append([1.08])
keys.append([-0.099752])

names.append("LShoulderPitch")
times.append([1.08])
keys.append([1.56157])

names.append("LShoulderRoll")
times.append([0.52, 1.08])
keys.append([0.570866, 0.642281])

names.append("LWristYaw")
times.append([1.08])
keys.append([0.133416])

names.append("RAnklePitch")
times.append([1.08])
keys.append([0.0890141])

names.append("RAnkleRoll")
times.append([1.08])
keys.append([0.11049])

names.append("RElbowRoll")
times.append([0.52, 1.08])
keys.append([0.801106, 1.46957])

names.append("RElbowYaw")
times.append([0.52, 1.08])
keys.append([0.596903, 0.230057])

names.append("RHand")
times.append([1.08])
keys.append([0.1892])

names.append("RHipPitch")
times.append([1.08])
keys.append([0.124212])

names.append("RHipRoll")
times.append([1.08])
keys.append([-0.116542])

names.append("RHipYawPitch")
times.append([1.08])
keys.append([-0.162562])

names.append("RKneePitch")
times.append([1.08])
keys.append([-0.091998])

names.append("RShoulderPitch")
times.append([1.08])
keys.append([1.47115])

names.append("RShoulderRoll")
times.append([0.52, 1.08])
keys.append([-0.570866, -0.642281])

names.append("RWristYaw")
times.append([1.08])
keys.append([-0.2102])

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
