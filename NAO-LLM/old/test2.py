import bpy

# Dati esportati da Choregraphe
names = ["HeadPitch", "HeadYaw", "LShoulderPitch", "LShoulderRoll",
         "LElbowYaw", "LElbowRoll", "LHand", "LShoulderPitch", "LShoulderRoll",
         "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RHand"]
times = [
    [0.52, 1.04], [0.52, 1.04], [0.48, 0.96], [0.48, 0.96],
    [0.48, 0.96], [0.48, 0.96], [0.48, 0.96], [0.48, 0.96],
    [0.56, 1], [0.56, 1], [0.56, 1], [0.56, 1], [0.56, 1]
]
keys = [
    [0.0398422, -0.073674], [0.0583338, 0.0767419], [1.38218, 1.39598], [-0.0674542, -0.226893],
    [-1.32073, -0.990921], [-1.01862, -1.32849], [0.686, 0.17], [1.37135, 1.36675],
    [0.021518, 0.226893], [1.41746, 0.964928], [1.0891, 1.33454], [0.788519, 0.24088]
]

# Mappa tra articolazioni di NAO e ossa Mixamo (rimuoviamo le gambe e i piedi)
nao_to_mixamo_map = {
    "HeadYaw": "Head",
    "HeadPitch": "Head",
    "LShoulderPitch": "LeftArm",
    "LShoulderRoll": "LeftArm",
    "LElbowYaw": "LeftForeArm",
    "LElbowRoll": "LeftForeArm",
    "LHand": "LeftHand",
    "RShoulderPitch": "RightArm",
    "RShoulderRoll": "RightArm",
    "RElbowYaw": "RightForeArm",
    "RElbowRoll": "RightForeArm",
    "RHand": "RightHand"
}


# Funzione per applicare keyframe di rotazione a un'osso
def apply_animation(armature, bone_name, times, values):
    for i, time in enumerate(times):
        # Convertire i valori da radianti a gradi (Blender usa i radianti)
        rotation = values[i]

        if bone_name in armature.pose.bones:
            bone = armature.pose.bones[bone_name]
            # Applica la rotazione sull'asse Z (modifica secondo necessità)
            bone.rotation_mode = 'XYZ'
            bone.rotation_euler[2] = rotation
            bone.keyframe_insert(data_path=f'pose.bones["{bone_name}"].rotation_euler', frame=time * 24)  # 24 FPS


# Verifica se l'oggetto selezionato è un'armatura
selected_obj = bpy.context.object

if selected_obj and selected_obj.type == 'ARMATURE':
    armature = selected_obj
    # Applica animazione alle ossa mappate
    for nao_joint, mixamo_bone in nao_to_mixamo_map.items():
        if mixamo_bone in armature.pose.bones:
            # Recupera i dati specifici per l'articolazione NAO
            joint_index = names.index(nao_joint)
            joint_times = times[joint_index]
            joint_keys = keys[joint_index]

            # Applica l'animazione al rig Mixamo
            apply_animation(armature, mixamo_bone, joint_times, joint_keys)
else:
    print("Errore: l'oggetto selezionato non è un'armatura.")