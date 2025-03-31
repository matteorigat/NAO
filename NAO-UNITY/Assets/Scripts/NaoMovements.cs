using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;
using System.Linq;

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
    
    private class Quaternions
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
    private float _coroutineTime = 0f;

    private Dictionary<string, float> startMotionKeys;
    private bool _isFirstMotion = true;
  
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

        _isFirstMotion = true;
        StartCoroutine(PlayMotion("Assets/Scripts/Gestures/GoToStand.txt"));
    }
    
    private void AddCurrentPositionToKeyframes(Dictionary<string, List<float>> motionKeys, Dictionary<string, List<float>> motionTimes)
    {
        if (_isFirstMotion)
        {
            _isFirstMotion = false;
            startMotionKeys = new Dictionary<string, float>();
            foreach (var jointName in motionKeys.Keys)
            {
                startMotionKeys[jointName] = 0f;
            }
        }
        
        foreach (var jointName in motionKeys.Keys)
        {
            motionKeys[jointName].Insert(0, startMotionKeys[jointName]);
            motionTimes[jointName].Insert(0, 0f);

            startMotionKeys[jointName] = motionKeys[jointName].Last();
        }
    }
    
    /*
    float NormalizeAngle(float angle)
    {
        angle = angle % 360;
        if (angle > 180)
            return angle - 360;
        if (angle <= -180)
            return angle + 360;
        return angle;
    }
    
    private float GetCurrentJointRotation(string jointName)
    {
        if (_jointMap.ContainsKey(jointName))
        {
            var joint = _jointMap[jointName];
            Quaternion offsetRotation = Quaternion.identity;

            if (_jointsOffset.ContainsKey(joint.jointTransform))
            {
                offsetRotation = _jointsOffset[joint.jointTransform];
            }

            // Applica l'offset alla rotazione locale
            Quaternion totalRotation = joint.jointTransform.localRotation * Quaternion.Inverse(offsetRotation);
            float angle = 0f;

            if (joint.rotationAxis == Vector3.right) // Pitch (x)
            {
                angle = totalRotation.x;
            }
            else if (joint.rotationAxis == Vector3.up) // Yaw (y)
            {
                angle = -totalRotation.y; // Inversione
            }
            else if (joint.rotationAxis == Vector3.forward) // Roll (z)
            {
                if (jointName == "LElbowRoll" || jointName == "RElbowRoll")
                {
                    angle = -totalRotation.z; // Inversione specifica
                }
                else
                {
                    angle = totalRotation.z;
                }
            }
            
            return Mathf.Deg2Rad * NormalizeAngle(angle);
        }
        return 0f;
    }
    
    
    /*private void AddCurrentPositionToKeyframes(Dictionary<string, List<float>> motionKeys, Dictionary<string, List<float>> motionTimes)
    {
        
        foreach (var jointName in motionKeys.Keys)
        {
            motionKeys[jointName].Insert(0, GetCurrentJointRotation(jointName));
            motionTimes[jointName].Insert(0, 0f);

            //startMotionKeys[jointName] = motionKeys[jointName].Last();
        }
    }*/
    
        
    public IEnumerator PlayMotion(String filePath, bool reverse = false)
    {
        float elapsedTime = 0f;
        float totalDuration = 0f; // Tempo massimo della sequenza

        var (motionKeys, motionTimes) = MotionExtractor.ExtractMotionData(filePath);
        
        if (motionKeys == null || motionTimes == null)
        {
            Debug.LogError("Errore nell'estrazione dei dati di movimento da: " + filePath);
            yield break; // Interrompi la coroutine se l'estrazione fallisce
        }
        
        
        // --- Aggiunta della posizione corrente al tempo 0 ---
        AddCurrentPositionToKeyframes(motionKeys, motionTimes);
        

        foreach (var entry in motionTimes)
        {
            foreach (float time in entry.Value)
            {
                if (time > totalDuration)
                {
                    totalDuration = time;
                }
            }
        }
        
        
        if (reverse)
        {
            // Inizializza i dizionari per i tempi e i keyframe invertiti
            var reversedTimes = new Dictionary<string, List<float>>();
            var reversedKeys = new Dictionary<string, List<float>>();

            foreach (var entry in motionTimes)
            {
                string jointName = entry.Key;
                List<float> jointTimes = entry.Value;

                // Invertiamo i tempi
                List<float> reversedJointTimes = jointTimes.Select(time => totalDuration - time).ToList();
    
                // Ordinare i tempi crescentemente
                reversedJointTimes.Sort();
                reversedTimes[jointName] = reversedJointTimes;

                // Invertiamo i keyframe mantenendo la corrispondenza con i nuovi tempi
                if (motionKeys.ContainsKey(jointName))
                {
                    List<float> jointKeys = motionKeys[jointName];

                    // Associare i keyframe ai nuovi tempi invertiti
                    Dictionary<float, float> timeKeyMap = jointTimes.Zip(jointKeys, (t, k) => new { t, k })
                        .ToDictionary(x => totalDuration - x.t, x => x.k);

                    // Estrarre i keyframe rispettando i nuovi tempi ordinati
                    List<float> reversedJointKeys = reversedJointTimes.Select(t => timeKeyMap[t]).ToList();
                    reversedKeys[jointName] = reversedJointKeys;
                }
            }
            
            motionKeys = reversedKeys;
            motionTimes = reversedTimes;
            
            /*for (int i = 0; i < motionKeys.Count; i++)
            {
                var jointName = motionKeys.Keys.ElementAt(i);

                List<float> jointKeys = motionKeys[jointName];
                List<float> jointTimes = motionTimes[jointName];

                Debug.Log($"Joint: {jointName} - Keys: {string.Join(", ", jointKeys)} - Times: {string.Join(", ", jointTimes)}");
                if(i == 3) break;
            }*/
        }
        
        _coroutineTime = totalDuration;

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
                    float angle = 1f - Interpolate(elapsedTime, motionTimes[jointName], motionKeys[jointName]);
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
                //Debug.Log(joint.Key);
                Quaternions rotations = joint.Value;
                
                Quaternion pitchRotation = Quaternion.identity;
                Quaternion yawRotation = Quaternion.identity;
                Quaternion rollRotation = Quaternion.identity;
                
                if (rotations.pitchRotation.HasValue)
                    pitchRotation = rotations.pitchRotation.Value;
                if (rotations.yawRotation.HasValue)
                    yawRotation = rotations.yawRotation.Value;
                if (rotations.rollRotation.HasValue)
                    rollRotation = rotations.rollRotation.Value;

                // Applica la rotazione finale
                if (_jointsOffset.ContainsKey(joint.Key))
                {
                    if (joint.Key.name == "Shoulder.L" || joint.Key.name == "Shoulder.R")
                        joint.Key.localRotation = rollRotation * pitchRotation * yawRotation * _jointsOffset[joint.Key]; // _jointsOffset[joint.Key]
                    else
                        joint.Key.localRotation = pitchRotation * yawRotation * rollRotation * _jointsOffset[joint.Key]; // _jointsOffset[joint.Key]
                }
                else joint.Key.localRotation = pitchRotation * yawRotation * rollRotation;

            }

            elapsedTime += Time.deltaTime;
            _coroutineTime = totalDuration - elapsedTime;
            yield return null;
        }

        _coroutineTime = 0f;
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
    
    public float IsPlayingTime()
    {
        return _coroutineTime;
    }
    
    void Update()
    {
        foreach (KeyCode key in new KeyCode[] { KeyCode.Q, KeyCode.A, KeyCode.Z, KeyCode.W, KeyCode.S, KeyCode.X, KeyCode.E, KeyCode.D, KeyCode.C, KeyCode.R, KeyCode.F, KeyCode.V })
        {
            if (Input.GetKeyDown(key))
            {
                StartCoroutine(PlayMotion(GetGesturePath(key)));
            }
        }
    }
    
    string GetGesturePath(KeyCode key)
    {
        switch (key)
        {
            case KeyCode.Q: return "Assets/Scripts/Gestures/Happiness1.txt";
            case KeyCode.A: return "Assets/Scripts/Gestures/Happiness2.txt";
            case KeyCode.Z: return "Assets/Scripts/Gestures/Happiness3.txt";
            case KeyCode.W: return "Assets/Scripts/Gestures/Sadness1.txt";
            case KeyCode.S: return "Assets/Scripts/Gestures/Sadness2.txt";
            case KeyCode.X: return "Assets/Scripts/Gestures/Sadness3.txt";
            case KeyCode.E: return "Assets/Scripts/Gestures/Anger1.txt";
            case KeyCode.D: return "Assets/Scripts/Gestures/Anger2.txt";
            case KeyCode.C: return "Assets/Scripts/Gestures/Anger3.txt";
            case KeyCode.R: return "Assets/Scripts/Gestures/Fear1.txt";
            case KeyCode.F: return "Assets/Scripts/Gestures/Fear2.txt";
            case KeyCode.V: return "Assets/Scripts/Gestures/Fear3.txt";
            default: return string.Empty;
        }
    }
}