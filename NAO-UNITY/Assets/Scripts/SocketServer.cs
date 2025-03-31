using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;
using System.Collections.Concurrent;
using System.Collections.Generic;

public class SocketServer : MonoBehaviour
{
    private TcpListener server;
    private Thread serverThread;
    private bool isRunning = false;

    public GameObject robotPrefab; // Riferimento al prefab del robot
    private EyeLEDController eyeLEDController;
    private volatile float faceX = float.NaN;
    private volatile float faceY = float.NaN;
    private NaoMovements NaoMovements;
    private String lastPose = "Stand";
    
    private List<string> gesturesList = new List<string>
    {
        "Happiness1", "Happiness2", "Happiness3",
        "Sadness1", "Sadness2", "Sadness3",
        "Anger1", "Anger2", "Anger3",
        "Fear1", "Fear2", "Fear3",
    };

    private ConcurrentQueue<string> messageQueue = new ConcurrentQueue<string>(); // Coda thread-safe
    
    
    // --- Variabili per la gestione della testa ---
    private Transform head;
    private Quaternion headInitialRotation;  // Rotazione iniziale della testa (al caricamento)
    private bool isHeadTrackingActive = true; // Stato del tracking della testa
    private bool isHeadAnimating = false;    // Indica se un'animazione (gesto) è in corso

    // Variabili per l'interpolazione
    private bool isInterpolating = false;
    private Quaternion interpolationStartRotation;
    private Quaternion interpolationTargetRotation;
    private float interpolationStartTime;
    private float interpolationDuration = 0.5f; 

    void Start()
    {
        if (robotPrefab != null)
        {
            eyeLEDController = robotPrefab.GetComponent<EyeLEDController>();
            NaoMovements = robotPrefab.GetComponent<NaoMovements>();
            head = robotPrefab.transform.Find("Armature/Torso/Head");
            if (head != null)
            {
                headInitialRotation = head.localRotation; // Salva la rotazione iniziale
            }
            else
            {
                Debug.LogError("Nodo Head non trovato!");
                return;
            }
        }
        else
        {
            Debug.LogError("Robot prefab non assegnato.");
            return;
        }
        

        StartServer();
    }

    void StartServer()
    {
        serverThread = new Thread(() =>
        {
            try
            {
                server = new TcpListener(IPAddress.Any, 47777); // Porta usata dal server
                server.Start();
                isRunning = true;
                Debug.Log("Server TCP avviato. In attesa di connessioni...");

                while (isRunning)
                {
                    if (server.Pending())
                    {
                        TcpClient client = server.AcceptTcpClient();
                        NetworkStream stream = client.GetStream();

                        byte[] buffer = new byte[1024];
                        int bytesRead = stream.Read(buffer, 0, buffer.Length);
                        if (bytesRead > 0)
                        {
                            string message = Encoding.UTF8.GetString(buffer, 0, bytesRead);

                            // Aggiungi il messaggio alla coda
                            messageQueue.Enqueue(message);
                        }

                        client.Close();
                    }
                }
            }
            catch (Exception e)
            {
                Debug.LogError("Errore nel server: " + e.Message);
            }
        });

        serverThread.IsBackground = true;
        serverThread.Start();
    }

    void Update()
    {
        // Esegui i comandi dalla coda nel thread principale
        while (messageQueue.TryDequeue(out string message))
        {
            ProcessMessage(message);
        }
        
        if (isHeadTrackingActive && !isHeadAnimating)  // Muovi SOLO se tracking attivo e nessuna animazione
        {
            if (isInterpolating)
            {
                InterpolateHead(); // Applica l'interpolazione
            }
            else
            {
                MoveHeadTowards(faceX, faceY); // O muovi verso il volto
            }
        }
        else if (!isHeadTrackingActive && isInterpolating) // Interpolazione verso la posizione iniziale
        {
            InterpolateHead();
        }
    }
    
    void MoveHeadTowards(float faceX, float faceY, float interpolationTime = 0.1f)
    {
        if (float.IsNaN(faceX) || float.IsNaN(faceY) || head == null) return;  
        
        // Normalizza le coordinate in un range [-1, 1]
        float normalizedX = -Mathf.Clamp((faceX / 1280f) * 2f - 1f , -1f, 1f); // Adatta la risoluzione della videocamera
        float normalizedY = Mathf.Clamp((faceY / 720f) * 2f - 1.3f , -1f, 1f);

        // Trova il nodo della testa
        /*Transform head = robotPrefab.transform.Find("Armature/Torso/Head");

        if (head != null)
        {
            // Calcola la nuova rotazione senza interpolazione
            float maxRotationAngle = 20f; // Angolo massimo di rotazione
            Quaternion targetRotation = Quaternion.Euler(0f, normalizedX * maxRotationAngle, normalizedY * maxRotationAngle);

            // Applica direttamente la rotazione senza interpolazione
            head.localRotation = targetRotation;
        }
        else
        {
            Debug.LogWarning("Nodo mixamorig:Head non trovato nella gerarchia del robot.");
        }*/

        float maxRotationAngle = 20f;
        Quaternion targetRotation = Quaternion.Euler(0f, normalizedX * maxRotationAngle, normalizedY * maxRotationAngle);

        // Avvia l'interpolazione verso la nuova posizione
        StartInterpolation(targetRotation, interpolationTime);
    }
    
    void StartInterpolation(Quaternion targetRotation, float duration)
    {
        if (head == null) return; // Controllo di sicurezza

        interpolationStartRotation = head.localRotation;
        interpolationTargetRotation = targetRotation;
        interpolationStartTime = Time.time;
        interpolationDuration = duration; // Imposta la durata specifica
        isInterpolating = true;
    }

    void InterpolateHead()
    {
        if (head == null)
        {
            isInterpolating = false; // Interrompi se head è nullo
            return;
        }


        float t = (Time.time - interpolationStartTime) / interpolationDuration;
        if (t < 1.0f)
        {
            head.localRotation = Quaternion.Slerp(interpolationStartRotation, interpolationTargetRotation, t);
        }
        else
        {
            head.localRotation = interpolationTargetRotation; // Imposta la rotazione finale
            isInterpolating = false;  // Ferma l'interpolazione
        }
    }

    void ProcessMessage(string message)
    {
        if (eyeLEDController == null) return;
        
        if (message.StartsWith("face_position:"))
        {
            string[] parts = message.Replace("face_position:", "").Split(',');
            if (parts.Length == 2 && float.TryParse(parts[0], out float faceX) && float.TryParse(parts[1], out float faceY))
            {
                if (isHeadTrackingActive)
                {
                    this.faceX = faceX;
                    this.faceY = faceY;
                }
                
            }
        }
        else
        {
            float timeLeft = 0f;
            switch (message)
            {
                case "listening":
                    Debug.Log("Comando Listening ricevuto!");
                    eyeLEDController.ListeningLEDs();
                    break;

                case "loading":
                    Debug.Log("Comando Loading ricevuto!");
                    eyeLEDController.isRotating = true;
                    StartCoroutine(eyeLEDController.RotateEyes());
                    StartCoroutine(NaoMovements.PlayMotion("Assets/Scripts/Gestures_new/HeadYes.txt"));
                    break;

                case "speaking":
                    Debug.Log("Comando Speaking ricevuto!");
                    eyeLEDController.isRotating = false;
                    eyeLEDController.SpeakingLEDs();
                    break;
                
                case "Stand":
                    if(lastPose == "Stand")
                        break;

                    timeLeft = NaoMovements.IsPlayingTime();
                    
                    //Debug.Log("LastPose: " + lastPose);
                    /*if(lastPose == "Fear3" || lastPose == "Sadness3")
                        Invoke(nameof(PlayGestureReverse), timeLeft);
                    else
                        Invoke(nameof(PlayGestureReverse2), timeLeft);
                        */
                    //Debug.Log("Performed stand: "+ message);
                    
                    Invoke(nameof(GoToStand), timeLeft);
                    
                    isHeadTrackingActive = true;
                    isHeadAnimating = false;
                    
                    if (!float.IsNaN(faceX) && !float.IsNaN(faceY))
                    {
                        MoveHeadTowards(faceX, faceY); // Usa MoveHeadTowards per calcolare la rotazione target
                    }
                    else
                    {
                        StartInterpolation(headInitialRotation, 0.5f);   // Interpola verso il centro
                    }
                    break;
                
                case var mess when gesturesList.Contains(mess): // Controllo se message è in gesturesList
                    
                    isHeadTrackingActive = false;
                    isHeadAnimating = true;
                    isInterpolating = false;

                    // 2. Salva la rotazione corrente della testa come punto di partenza per l'interpolazione
                    if (head != null)
                    {
                        interpolationStartRotation = head.localRotation;
                        //StartInterpolation(headInitialRotation, 0.5f);
                    }

                    //Debug.Log("Perform gesture: " + message);
                    timeLeft = NaoMovements.IsPlayingTime();
                    if(mess == "Stand")
                        Invoke(nameof(GoToStand), timeLeft);
                    Invoke(nameof(PlayGesture), timeLeft);
                    lastPose = message;
                    break;

                default:
                    Debug.Log("Comando non riconosciuto: " + message);
                    break;
            }
        }
    }
    
    void PlayGesture()
    {
        if (NaoMovements != null)
        {
            StartCoroutine(NaoMovements.PlayMotion("Assets/Scripts/Gestures_new/" + lastPose + ".txt"));

        }
    }
    
    void GoToStand()
    {
        if (NaoMovements != null)
        {
            StartCoroutine(NaoMovements.PlayMotion("Assets/Scripts/Gestures_new/GoToSTand.txt"));
            lastPose = "Stand";
        }
    }
    
    void PlayGestureReverse()
    {
        if (NaoMovements != null)
        {
            StartCoroutine(NaoMovements.PlayMotion("Assets/Scripts/Gestures/" + lastPose + "reverse.txt"));
            lastPose = "Stand";
        }
    }
    
    void PlayGestureReverse2()
    {
        if (NaoMovements != null)
        {
            StartCoroutine(NaoMovements.PlayMotion("Assets/Scripts/Gestures/"+ lastPose +".txt", true));
            lastPose = "Stand";

        }
    }

    void OnApplicationQuit()
    {
        isRunning = false;
        if (server != null)
        {
            server.Stop();
        }
        if (serverThread != null && serverThread.IsAlive)
        {
            serverThread.Abort();
        }
    }
}