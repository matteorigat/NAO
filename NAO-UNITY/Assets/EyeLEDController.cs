using System.Collections;
using UnityEngine;

public class EyeLEDController : MonoBehaviour
{
    // Riferimenti ai 8 spicchi di LED per occhio (metti qui i riferimenti degli spicchi)
    public Renderer[] leftEyeLEDs;
    public Renderer[] rightEyeLEDs;

    // Colori per i LED accesi e spenti
    public Color ListeningColorEmission = Color.green;
    public Color ListeningColor = new Color(0.639f, 1f, 0.659f);
    public Color ledOffColor = Color.white;  // Colore quando il LED è spento
    public Color RotationColorEmission = Color.blue;
    public Color RotationColor = new Color(0.529f, 0.808f, 0.922f);
    public Color SpeakingColorEmission = Color.white;
    public Color SpeakingColor = Color.white;

    // Durata del singolo passo dell'animazione
    public float ledOnDuration = 0.1f;
    private volatile bool isRotating = false;
    
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

    // Funzione per spegnere tutti i LED di un occhio
    public void TurnOffAllLEDs()
    {
        foreach (var led in leftEyeLEDs)
        {
            led.material.SetColor("_EmissionColor", ledOffColor);
            led.material.SetColor("_Color", Color.white);
        }
        
        foreach (var led in rightEyeLEDs)
        {
            led.material.SetColor("_EmissionColor", ledOffColor);
            led.material.SetColor("_Color", Color.white);
        }
    }
    
    public IEnumerator RotateEyes()
    {
        // Lista dei LED in ordine per simulare il movimento circolare
        Renderer[][] ledPairs = new Renderer[][]
        {
            new Renderer[] { leftEyeLEDs[0], rightEyeLEDs[7] },
            new Renderer[] { leftEyeLEDs[1], rightEyeLEDs[6] },
            new Renderer[] { leftEyeLEDs[2], rightEyeLEDs[5] },
            new Renderer[] { leftEyeLEDs[3], rightEyeLEDs[4] },
            new Renderer[] { leftEyeLEDs[4], rightEyeLEDs[3] },
            new Renderer[] { leftEyeLEDs[5], rightEyeLEDs[2] },
            new Renderer[] { leftEyeLEDs[6], rightEyeLEDs[1] },
            new Renderer[] { leftEyeLEDs[7], rightEyeLEDs[0] }
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
            ListeningLEDs();
        }
        if (Input.GetKeyDown(KeyCode.Alpha2))
        {
            SpeakingLEDs();
        }
        if (Input.GetKeyDown(KeyCode.Alpha3))
        {
            isRotating = true;
            StartCoroutine(RotateEyes());
        }
        if (Input.GetKeyDown(KeyCode.Alpha4))
        {
            isRotating = false;
            TurnOffAllLEDs();
        }
    }
}
