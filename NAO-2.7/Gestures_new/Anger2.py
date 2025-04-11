# Choregraphe simplified export in Python.
from naoqi import ALProxy
names = list()
times = list()
keys = list()

names.append("HeadPitch")
times.append([0.96])
keys.append([0.199378])

names.append("HeadYaw")
times.append([0.96])
keys.append([-0.00310993])

names.append("LAnklePitch")
times.append([0.96])
keys.append([0.0873961])

names.append("LAnkleRoll")
times.append([0.96])
keys.append([-0.10427])

names.append("LElbowRoll")
times.append([0.96])
keys.append([-0.0551819])

names.append("LElbowYaw")
times.append([0.96])
keys.append([-1.47268])

names.append("LHand")
times.append([0.96])
keys.append([0.0164])

names.append("LHipPitch")
times.append([0.96])
keys.append([0.12583])

names.append("LHipRoll")
times.append([0.96])
keys.append([0.11049])

names.append("LHipYawPitch")
times.append([0.96])
keys.append([-0.162562])

names.append("LKneePitch")
times.append([0.96])
keys.append([-0.099752])

names.append("LShoulderPitch")
times.append([0.96])
keys.append([1.42811])

names.append("LShoulderRoll")
times.append([0.96])
keys.append([0.312894])

names.append("LWristYaw")
times.append([0.96])
keys.append([0.0996681])

names.append("RAnklePitch")
times.append([0.96])
keys.append([0.0890141])

names.append("RAnkleRoll")
times.append([0.96])
keys.append([0.11049])

names.append("RElbowRoll")
times.append([0.96])
keys.append([0.0552659])

names.append("RElbowYaw")
times.append([0.96])
keys.append([1.4726])

names.append("RHand")
times.append([0.96])
keys.append([0.0136])

names.append("RHipPitch")
times.append([0.96])
keys.append([0.124212])

names.append("RHipRoll")
times.append([0.96])
keys.append([-0.116542])

names.append("RHipYawPitch")
times.append([0.96])
keys.append([-0.162562])

names.append("RKneePitch")
times.append([0.96])
keys.append([-0.091998])

names.append("RShoulderPitch")
times.append([0.96])
keys.append([1.44354])

names.append("RShoulderRoll")
times.append([0.96])
keys.append([-0.31758])

names.append("RWristYaw")
times.append([0.96])
keys.append([0.076658])

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
