from naoqi import ALProxy
import time

# Connessione ai proxy
motion = ALProxy("ALMotion", "127.0.0.1", 9559)
posture = ALProxy("ALRobotPosture", "127.0.0.1", 9559)

# Imposta la postura iniziale del robot
posture.goToPosture("Stand", 0.5)

# Definisci il movimento per alzare la mano
motion.setStiffnesses("LArm", 1.0)
motion.setStiffnesses("RArm", 1.0)

# Loop di saluto
while True:
    # Solleva la mano destra (RArm)
    motion.setAngles("RShoulderPitch", 1.0, 0.2)
    motion.setAngles("RShoulderRoll", -0.2, 0.2)
    motion.setAngles("RElbowYaw", 1.5, 0.2)
    motion.setAngles("RElbowRoll", 0.0, 0.2)

    # Pausa per tenere la mano sollevata per un po'
    time.sleep(1)

    # Abbassa la mano
    motion.setAngles("RShoulderPitch", 0.0, 0.2)
    motion.setAngles("RShoulderRoll", 0.0, 0.2)
    motion.setAngles("RElbowYaw", 0.0, 0.2)
    motion.setAngles("RElbowRoll", 0.0, 0.2)

    # Pausa per la transizione
    time.sleep(1)