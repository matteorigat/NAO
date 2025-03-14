# Choregraphe simplified export in Python.
from naoqi import ALProxy
names = list()
times = list()
keys = list()

names.append("HeadPitch")
times.append([0, 1.36])
keys.append([-0.164672, 0.431013])

names.append("HeadYaw")
times.append([0, 1.36])
keys.append([-0.00528999, -0.00310993])

names.append("LAnklePitch")
times.append([0, 1.36])
keys.append([0.0871523, 0.0873961])

names.append("LAnkleRoll")
times.append([0, 1.36])
keys.append([-0.107881, -0.10427])

names.append("LElbowRoll")
times.append([0, 1.36])
keys.append([-0.423813, -0.777696])

names.append("LElbowYaw")
times.append([0, 1.36])
keys.append([-1.21097, -1.20116])

names.append("LHand")
times.append([0, 1.36])
keys.append([0.292717, 0.2792])

names.append("LHipPitch")
times.append([0, 1.36])
keys.append([0.12407, 0.12583])

names.append("LHipRoll")
times.append([0, 1.36])
keys.append([0.115978, 0.11049])

names.append("LHipYawPitch")
times.append([0, 1.36])
keys.append([-0.16949, -0.162562])

names.append("LKneePitch")
times.append([0, 1.36])
keys.append([-0.0920459, -0.099752])

names.append("LShoulderPitch")
times.append([0, 1.36])
keys.append([1.43826, 1.44652])

names.append("LShoulderRoll")
times.append([0, 1.36])
keys.append([0.229205, 0.00916195])

names.append("LWristYaw")
times.append([0, 1.36])
keys.append([0.0969078, 0.0996681])

names.append("RAnklePitch")
times.append([0, 1.36])
keys.append([0.0871523, 0.0890141])

names.append("RAnkleRoll")
times.append([0, 1.36])
keys.append([0.107877, 0.11049])

names.append("RElbowRoll")
times.append([0, 1.36])
keys.append([0.424029, 0.774711])

names.append("RElbowYaw")
times.append([0, 1.36])
keys.append([1.20349, 1.20875])

names.append("RHand")
times.append([0, 1.36])
keys.append([0.291444, 0.2824])

names.append("RHipPitch")
times.append([0, 1.36])
keys.append([0.12407, 0.124212])

names.append("RHipRoll")
times.append([0, 1.36])
keys.append([-0.115972, -0.116542])

names.append("RHipYawPitch")
times.append([0, 1.36])
keys.append([-0.16949, -0.162562])

names.append("RKneePitch")
times.append([0, 1.36])
keys.append([-0.0920459, -0.091998])

names.append("RShoulderPitch")
times.append([0, 1.36])
keys.append([1.4411, 1.44354])

names.append("RShoulderRoll")
times.append([0, 1.36])
keys.append([-0.23216, 0.00455999])

names.append("RWristYaw")
times.append([0, 1.36])
keys.append([0.0949686, 0.0735901])

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
