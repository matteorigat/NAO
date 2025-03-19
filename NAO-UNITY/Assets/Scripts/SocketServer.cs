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
    //private Animator robotAnimator; // Riferimento al componente Animator
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

    void Start()
    {
        if (robotPrefab != null)
        {
            //robotAnimator = robotPrefab.GetComponent<Animator>();
            eyeLEDController = robotPrefab.GetComponent<EyeLEDController>();
            NaoMovements = robotPrefab.GetComponent<NaoMovements>();
            
            //if (robotAnimator == null)
            //{
             //   Debug.LogError("Il prefab del robot non ha un componente Animator.");
             //   return;
            //} 
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
                server = new TcpListener(IPAddress.Any, 50000); // Porta usata dal server
                server.Start();
                isRunning = true;
                Debug.Log("Server TCP avviato. In attesa di connessioni...");

                while (isRunning)
                {
                    if (server.Pending())
                    {
                        TcpClient client = server.AcceptTcpClient();
                        //Debug.Log("Client connesso!");
                        NetworkStream stream = client.GetStream();

                        byte[] buffer = new byte[1024];
                        int bytesRead = stream.Read(buffer, 0, buffer.Length);
                        if (bytesRead > 0)
                        {
                            string message = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                            //Debug.Log("Messaggio ricevuto: " + message);

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
        
        //robotAnimator.enabled = false;
        MoveHeadTowards(faceX, faceY);
        //robotAnimator.enabled = true;
    }
    
    void MoveHeadTowards(float faceX, float faceY)
    {
        if (float.IsNaN(faceX) || float.IsNaN(faceY))
            return;  
        
        // Normalizza le coordinate in un range [-1, 1]
        float normalizedX = -Mathf.Clamp((faceX / 1280f) * 2f - 1f , -1f, 1f); // Adatta la risoluzione della videocamera
        float normalizedY = Mathf.Clamp((faceY / 720f) * 2f - 1.3f , -1f, 1f);

        // Trova il nodo della testa
        Transform head = robotPrefab.transform.Find("Armature/Torso/Head");

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
        }
    }

    void ProcessMessage(string message)
    {
        //if (robotAnimator == null || eyeLEDController == null) return;
        if (eyeLEDController == null) return;
        
        //robotAnimator.CrossFade("empty_animation", 0f); 
        
        if (message.StartsWith("face_position:"))
        {
            string[] parts = message.Replace("face_position:", "").Split(',');
            if (parts.Length == 2 && float.TryParse(parts[0], out float faceX) && float.TryParse(parts[1], out float faceY))
            {
                this.faceX = faceX;
                this.faceY = faceY;
                
            }
        }
        else
        {
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
                    //robotAnimator.CrossFade("Armature|HeadYes", 0.25f);
                    break;

                case "speaking":
                    Debug.Log("Comando Speaking ricevuto!");
                    eyeLEDController.isRotating = false;
                    eyeLEDController.SpeakingLEDs();
                    //robotAnimator.CrossFade("Armature_GatherBothHandsInFront_001", 0.25f);
                    break;
                
                case "Stand":
                    if(lastPose == "Stand")
                        break;
                    
                    //Debug.Log("LastPose: " + lastPose);
                    if(lastPose == "Fear3" || lastPose == "Sadness3")
                        StartCoroutine(NaoMovements.PlayMotion("Assets/Scripts/Gestures/"+ lastPose +"reverse.txt"));
                    else
                        StartCoroutine(NaoMovements.PlayMotion("Assets/Scripts/Gestures/"+ lastPose +".txt", true));
                    //Debug.Log("Performed stand: "+ message);
                    lastPose = "Stand";
                    break;
                
                case var mess when gesturesList.Contains(mess): // Controllo se message è in gesturesList
                    //Debug.Log("Perform gesture: " + message);
                    StartCoroutine(NaoMovements.PlayMotion("Assets/Scripts/Gestures/" + message + ".txt"));
                    lastPose = message;
                    break;

                default:
                    Debug.Log("Comando non riconosciuto: " + message);
                    break;
            }
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