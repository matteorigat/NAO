using System.Collections;
using UnityEngine;

public class EyeLEDController : MonoBehaviour
{
    // Riferimenti ai 8 spicchi di LED per occhio (metti qui i riferimenti degli spicchi)
    public Renderer[] leftEyeLEDs;
    public Renderer[] rightEyeLEDs;

    // Colori per i LED accesi e spenti
    private  Color ListeningColorEmission = Color.green;
    private  Color ListeningColor = new Color(0.639f, 1f, 0.659f);
    private  Color RotationColorEmission = Color.blue;
    private  Color RotationColor = new Color(0.529f, 0.808f, 0.922f);
    private  Color SpeakingColorEmission = Color.white;
    private  Color SpeakingColor = Color.white;
    private Color ledOffColor;
    private Color ledOffColorEmission; 

    // Durata del singolo passo dell'animazione
    private float ledOnDuration = 0.1f;
    public volatile bool isRotating = false;
    
    
    void Start()
    {
        // Store initial LED states
        foreach (Renderer led in leftEyeLEDs)
        {
            ledOffColor = led.material.GetColor("_Color");
            ledOffColorEmission = led.material.GetColor("_EmissionColor");
            break;
        }
    }
    // Funzione per accendere tutti i LED di un occhio
    public void ListeningLEDs()
    {
        foreach (var led in leftEyeLEDs)
        {
            led.material.SetColor("_EmissionColor", ListeningColorEmission * 3f);
            led.material.SetColor("_Color", ListeningColor);
        }
        
        foreach (var led in rightEyeLEDs)
        {
            led.material.SetColor("_EmissionColor", ListeningColorEmission * 3f);
            led.material.SetColor("_Color", ListeningColor);
        }
    }
    
    public void SpeakingLEDs()
    {
        foreach (var led in leftEyeLEDs)
        {
            led.material.SetColor("_EmissionColor", SpeakingColorEmission);
            led.material.SetColor("_Color", SpeakingColor);
        }
        
        foreach (var led in rightEyeLEDs)
        {
            led.material.SetColor("_EmissionColor", SpeakingColorEmission);
            led.material.SetColor("_Color", SpeakingColor);
        }
    }

    public void TurnOffAllLEDs()
    {
        foreach (var led in leftEyeLEDs)
        {
            led.material.SetColor("_EmissionColor", ledOffColorEmission);
            led.material.SetColor("_Color", ledOffColor);
        }
        
        foreach (var led in rightEyeLEDs)
        {
            led.material.SetColor("_EmissionColor", ledOffColorEmission);
            led.material.SetColor("_Color", ledOffColor);
        }
    }
    
    public IEnumerator RotateEyes()
    {
        // Lista dei LED in ordine per simulare il movimento circolare
        Renderer[][] ledPairs = new Renderer[][]
        {
            new Renderer[] { leftEyeLEDs[0], rightEyeLEDs[0] },
            new Renderer[] { leftEyeLEDs[1], rightEyeLEDs[1] },
            new Renderer[] { leftEyeLEDs[2], rightEyeLEDs[2] },
            new Renderer[] { leftEyeLEDs[3], rightEyeLEDs[3] },
            new Renderer[] { leftEyeLEDs[4], rightEyeLEDs[4] },
            new Renderer[] { leftEyeLEDs[5], rightEyeLEDs[5] },
            new Renderer[] { leftEyeLEDs[6], rightEyeLEDs[6] },
            new Renderer[] { leftEyeLEDs[7], rightEyeLEDs[7] }
        };
        
        while (isRotating)
        {
            // Accendi il LED di ciascun spicchio, alternando tra occhio sinistro e destro
            for (int i = 0; i < ledPairs.Length; i++)
            {
                // Spegni i LED precedenti
                TurnOffAllLEDs();
                if(!isRotating)
                    break;

                // Accendi il LED del prossimo spicchio e il LED adiacente
                ledPairs[i][0].material.SetColor("_EmissionColor", RotationColorEmission);
                ledPairs[(i+1)%ledPairs.Length][0].material.SetColor("_EmissionColor", RotationColorEmission);
                ledPairs[i][1].material.SetColor("_EmissionColor", RotationColorEmission);
                ledPairs[(i+1)%ledPairs.Length][1].material.SetColor("_EmissionColor", RotationColorEmission);
                ledPairs[i][0].material.SetColor("_Color", RotationColor);
                ledPairs[(i+1)%ledPairs.Length][0].material.SetColor("_Color", RotationColor);
                ledPairs[i][1].material.SetColor("_Color", RotationColor);
                ledPairs[(i+1)%ledPairs.Length][1].material.SetColor("_Color", RotationColor);

                // Aspetta per la durata del passo
                yield return new WaitForSeconds(ledOnDuration);
            }
        } 
        
        TurnOffAllLEDs();
    }
    
    void Update()
    {
        
        if (Input.GetKeyDown(KeyCode.Alpha1))
        {
            isRotating = false;
            ListeningLEDs();
        }
        if (Input.GetKeyDown(KeyCode.Alpha2))
        {
            isRotating = true;
            StartCoroutine(RotateEyes());
        }
        if (Input.GetKeyDown(KeyCode.Alpha3))
        {
            isRotating = false;
            SpeakingLEDs();
        }
        if (Input.GetKeyDown(KeyCode.Alpha4))
        {
            isRotating = false;
            TurnOffAllLEDs();
        }
    }
}
