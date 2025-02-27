using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;

public class NaoMovements : MonoBehaviour
{
    [System.Serializable]
    public class JointMovement
    {
        public string jointName;
        public Transform jointTransform;
        public Vector3 rotationAxis;  // L'asse da ruotare
    }
    
    [System.Serializable]
    public class JointMovementHand
    {
        public string jointName;
        public List<Transform> jointTransforms;
    }
    
    public class Quaternions
    {
        public Quaternion? pitchRotation;
        public Quaternion? yawRotation;
        public Quaternion? rollRotation;
    }

    [SerializeField] public List<JointMovement> joints; // Lista dei giunti configurabili
    [SerializeField] public List<JointMovementHand> jointsHand; 
    private Dictionary<string, JointMovement> _jointMap;
    private Dictionary<string, JointMovementHand> _jointMapHand;
    private Dictionary<Transform, Quaternions> _jointsUnion;
    private Dictionary<Transform, Quaternion> _jointsOffset;
  
    void Start()
    {
        _jointMap = new Dictionary<string, JointMovement>();
        _jointMapHand = new Dictionary<string, JointMovementHand>();
        _jointsUnion = new Dictionary<Transform, Quaternions>();
        _jointsOffset = new Dictionary<Transform, Quaternion>();
        
        Quaternion rotation;
        foreach (var joint in joints)
        {
            _jointMap[joint.jointName] = joint;
            
            // Salva la rotazione iniziale di ogni giunto
            rotation = joint.jointTransform.localRotation;
            if (!_jointsOffset.ContainsKey(joint.jointTransform))
            {
                _jointsOffset[joint.jointTransform] = rotation;
            }
        }
        
        foreach (var jointHand in jointsHand)
        {
            _jointMapHand[jointHand.jointName] = jointHand;
        }
        
        StartCoroutine(PlayMotion());
    }
    
        
    IEnumerator PlayMotion()
    {
        
        // Dati estratti da Choregraphe
        /*
        Dictionary<string, List<float>> motionKeys = new Dictionary<string, List<float>>
        {
            { "HeadPitch", new List<float> { 0f, 0f } },
            { "HeadYaw", new List<float> { 0f, 0f } },
            
            { "LShoulderPitch", new List<float> { 0f, 0f} },
            { "LShoulderRoll", new List<float> { 0f, 0f } },
            { "LElbowYaw", new List<float> { 0f, 0f} },
            { "LElbowRoll", new List<float> { 0f, 0f } },
            { "LWristYaw", new List<float> { 0f, 0f } },
            { "LHand", new List<float> { 0f, 1f } },
            
            
            { "RShoulderPitch", new List<float> { 0f, 0f} },
            { "RShoulderRoll", new List<float> { 0f, 0f } },
            { "RElbowYaw", new List<float> { 0f, 0f} },
            { "RElbowRoll", new List<float> { 0f, 0f } },
            { "RWristYaw", new List<float> { 0f, 0f } },
            { "RHand", new List<float> { 0f, 1f } },
        };

        Dictionary<string, List<float>> motionTimes = new Dictionary<string, List<float>>
        {
            { "HeadPitch", new List<float> { 0.5f, 1f} },
            { "HeadYaw", new List<float> { 0.5f, 1f } },
            
            { "LShoulderPitch", new List<float> { 0.5f, 1f } },
            { "LShoulderRoll", new List<float> { 0.5f, 1f} },
            { "LElbowYaw", new List<float> { 0.5f, 1f} },
            { "LElbowRoll", new List<float> { 0.5f, 1f } },
            { "LWristYaw", new List<float> { 0.5f, 1f } },
            { "LHand", new List<float> { 0.5f, 1f } },
            
            
            { "RShoulderPitch", new List<float> { 0.5f, 1f } },
            { "RShoulderRoll", new List<float> { 0.5f, 1f} },
            { "RElbowYaw", new List<float> { 0.5f, 1f} },
            { "RElbowRoll", new List<float> { 0.5f, 1f } },
            { "RWristYaw", new List<float> { 0.5f, 1f } },
            { "RHand", new List<float> { 0.5f, 1f } },
        };
        */
            
        string filePath = "Assets/motion_data.txt";

        var (motionKeys, motionTimes) = MotionExtractor.ExtractMotionData(filePath);
        
        Debug.Log("Motion Keys:");
        foreach (var entry in motionKeys)
        {
            Debug.Log($"Joint: {entry.Key} - Keys: {string.Join(", ", entry.Value)}");
        }

        Debug.Log("\nMotion Times:");
        foreach (var entry in motionTimes)
        {
            Debug.Log($"Joint: {entry.Key} - Times: {string.Join(", ", entry.Value)}");
        }
        

        float elapsedTime = 0f;
        float totalDuration = 4f; // Tempo massimo della sequenza

        while (elapsedTime < totalDuration)
        {
            foreach (var jointName in motionKeys.Keys)
            {
                if (_jointMap.ContainsKey(jointName))
                {
                    JointMovement joint = _jointMap[jointName];
                    float angle = Interpolate(elapsedTime, motionTimes[jointName], motionKeys[jointName]);
                    //if (angle == 0f) continue;
                    float angleInDegrees = Mathf.Rad2Deg * angle;
                    
                    if (!_jointsUnion.ContainsKey(joint.jointTransform))
                    {
                        _jointsUnion[joint.jointTransform] = new Quaternions();
                    }

                    // Calcolare la rotazione per Pitch, Yaw, Roll separatamente
                    if (joint.rotationAxis == Vector3.right) // Pitch (x)
                        _jointsUnion[joint.jointTransform].pitchRotation = Quaternion.Euler(angleInDegrees, 0f, 0f);
                    else if (joint.rotationAxis == Vector3.up) // Yaw (y)
                        _jointsUnion[joint.jointTransform].yawRotation = Quaternion.Euler(0f, -angleInDegrees, 0f);
                    else if (joint.rotationAxis == Vector3.forward) // Roll (z)
                            if ( jointName == "LElbowRoll" || jointName == "RElbowRoll")
                                _jointsUnion[joint.jointTransform].rollRotation = Quaternion.Euler(0f, 0f, -angleInDegrees); 
                            else _jointsUnion[joint.jointTransform].rollRotation = Quaternion.Euler(0f, 0f, angleInDegrees);
                }
                else if (_jointMapHand.ContainsKey(jointName))
                {
                    JointMovementHand hand = _jointMapHand[jointName];
                    float angle = Interpolate(elapsedTime, motionTimes[jointName], motionKeys[jointName]);
                    float angleInDegrees = Mathf.Rad2Deg * angle;
                    int count = 0;
                    foreach (var joint in hand.jointTransforms)
                    {
                        if (!_jointsUnion.ContainsKey(joint))
                        {
                            _jointsUnion[joint] = new Quaternions();
                        }

                        float adjustedAngle = (count < 6) ? -angleInDegrees*1.3f : angleInDegrees*0.5f;
                        _jointsUnion[joint].pitchRotation = Quaternion.Euler(adjustedAngle, 0f, 0f);
                        float rotationAngle = (count < 6) ? 0f : 20f;
                        _jointsUnion[joint].rollRotation = Quaternion.Euler(0f, rotationAngle, 0.5f);
    
                        count++; // Incrementa il contatore
                    }
                }
            }
            
            foreach (var joint in _jointsUnion)
            {
                Debug.Log(joint.Key);
                Quaternions rotations = joint.Value;
                
                Quaternion pitchRotation = Quaternion.identity;
                Quaternion yawRotation = Quaternion.identity;
                Quaternion rollRotation = Quaternion.identity;
                
                if (rotations.pitchRotation.HasValue)
                    pitchRotation = rotations.pitchRotation.Value;
                /*else
                    foreach (var jointAx in _jointMap)
                        if (jointAx.Value.jointTransform == joint.Key && jointAx.Value.rotationAxis == Vector3.right)
                            pitchRotation = Quaternion.Euler(Mathf.Rad2Deg * jointAx.Value.initialAngleOffset, 0f, 0f);
                */
                if (rotations.yawRotation.HasValue)
                    yawRotation = rotations.yawRotation.Value;
                /*else
                   foreach (var jointAx in _jointMap)
                        if (jointAx.Value.jointTransform == joint.Key && jointAx.Value.rotationAxis == Vector3.up)
                            yawRotation = Quaternion.Euler(0f, Mathf.Rad2Deg * jointAx.Value.initialAngleOffset, 0f);
                */
                if (rotations.rollRotation.HasValue)
                    rollRotation = rotations.rollRotation.Value;
                /*else
                    foreach (var jointAx in _jointMap)
                        if (jointAx.Value.jointTransform == joint.Key && jointAx.Value.rotationAxis == Vector3.forward)
                            rollRotation = Quaternion.Euler(0f, 0f, Mathf.Rad2Deg * jointAx.Value.initialAngleOffset);
                */

                // Applica la rotazione finale
                if (_jointsOffset.ContainsKey(joint.Key))
                    joint.Key.localRotation = pitchRotation * yawRotation * rollRotation * _jointsOffset[joint.Key];
                else joint.Key.localRotation = pitchRotation * yawRotation * rollRotation;

            }

            elapsedTime += Time.deltaTime;
            yield return null;
        }
    }

    float Interpolate(float time, List<float> times, List<float> values)
    {
        if (times.Count == 0) return 0f;  // Gestisci caso in cui la lista sia vuota

        // Se time è fuori dall'intervallo, restituisci il primo o l'ultimo valore
        if (time <= times[0]) return values[0];
        if (time >= times[times.Count - 1]) return values[values.Count - 1];

        // Trova l'intervallo appropriato (ricerca binaria per efficienza)
        int index = System.Array.BinarySearch(times.ToArray(), time);
        if (index < 0) index = ~index - 1;  // Indice dell'intervallo precedente

        // Interpolazione lineare
        float t = (time - times[index]) / (times[index + 1] - times[index]);
        return Mathf.Lerp(values[index], values[index + 1], t);
    }
}