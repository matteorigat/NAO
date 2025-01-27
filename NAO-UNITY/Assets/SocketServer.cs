using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;
using System.Collections.Concurrent;

public class SocketServer : MonoBehaviour
{
    private TcpListener server;
    private Thread serverThread;
    private bool isRunning = false;

    public GameObject robotPrefab; // Riferimento al prefab del robot
    private Animator robotAnimator; // Riferimento al componente Animator
    private EyeLEDController eyeLEDController;

    private ConcurrentQueue<string> messageQueue = new ConcurrentQueue<string>(); // Coda thread-safe

    void Start()
    {
        if (robotPrefab != null)
        {
            robotAnimator = robotPrefab.GetComponent<Animator>();
            eyeLEDController = robotPrefab.GetComponent<EyeLEDController>(); 
            if (robotAnimator == null)
            {
                Debug.LogError("Il prefab del robot non ha un componente Animator.");
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
                server = new TcpListener(IPAddress.Any, 65432); // Porta usata dal server
                server.Start();
                isRunning = true;
                Debug.Log("Server TCP avviato. In attesa di connessioni...");

                while (isRunning)
                {
                    if (server.Pending())
                    {
                        TcpClient client = server.AcceptTcpClient();
                        Debug.Log("Client connesso!");
                        NetworkStream stream = client.GetStream();

                        byte[] buffer = new byte[1024];
                        int bytesRead = stream.Read(buffer, 0, buffer.Length);
                        if (bytesRead > 0)
                        {
                            string message = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                            Debug.Log("Messaggio ricevuto: " + message);

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
    }

    void ProcessMessage(string message)
    {
        if (robotAnimator == null || eyeLEDController == null) return;
        
        //robotAnimator.CrossFade("empty_animation", 0f); 

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
                robotAnimator.CrossFade("Armature|HeadYes", 0.25f);
                break;

            case "speaking":
                Debug.Log("Comando Speaking ricevuto!");
                eyeLEDController.isRotating = false;
                eyeLEDController.SpeakingLEDs();
                robotAnimator.CrossFade("Armature|GatherBothHandsInFront_001", 0.25f);
                break;
            
            default:
                Debug.LogWarning("Comando non riconosciuto: " + message);
                break;
            
            // case "HeadYes":
            //     Debug.Log("Comando HeadYes ricevuto!");
            //     break;
            //
            // case "Exlamation":
            //     Debug.Log("Comando Exlamation ricevuto!");
            //     robotAnimator.CrossFade("Armature|Exlamation", 0.25f);
            //     break;
            //
            // case "GatherBothHandsInFront_001":
            //     Debug.Log("Comando GatherBothHandsInFront_001 ricevuto!");
            //     robotAnimator.CrossFade("Armature|GatherBothHandsInFront_001", 0.25f);
            //
            
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