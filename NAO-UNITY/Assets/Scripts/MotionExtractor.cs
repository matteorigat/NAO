using System;
using System.IO;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using UnityEngine;

public class MotionExtractor
{
    // Funzione modificata che restituisce i dizionari
    public static (Dictionary<string, List<float>> motionKeys, Dictionary<string, List<float>> motionTimes) ExtractMotionData(string filePath)
    {
        
        if (!File.Exists(filePath))
        {
            Debug.Log("File non trovato: " + filePath);
            return (null, null);
        }
        
        // Dizionari per memorizzare i dati
        Dictionary<string, List<float>> motionKeys = new Dictionary<string, List<float>>();
        Dictionary<string, List<float>> motionTimes = new Dictionary<string, List<float>>();
        
        try
        {
            // Leggere il contenuto del file
            string[] lines = File.ReadAllLines(filePath);

            string currentName = "";
            List<float> currentTimes = null;
            List<float> currentKeys = null;

            // Pattern per estrarre i nomi, i tempi e i valori delle chiavi
            Regex namePattern = new Regex(@"names\.append\(\""(.*?)\""\)");
            Regex timePattern = new Regex(@"times\.append\(\[(.*?)\]\)");
            Regex keyPattern = new Regex(@"keys\.append\(\[(.*?)\]\)");

            foreach (var line in lines)
            {
                // Controlla per i nomi dei joint
                Match nameMatch = namePattern.Match(line);
                if (nameMatch.Success)
                {
                    currentName = nameMatch.Groups[1].Value;
                    continue;
                }

                // Controlla per i tempi
                Match timeMatch = timePattern.Match(line);
                if (timeMatch.Success)
                {
                    currentTimes = ParseFloatList(timeMatch.Groups[1].Value);
                    continue;
                }

                // Controlla per le chiavi
                Match keyMatch = keyPattern.Match(line);
                if (keyMatch.Success)
                {
                    currentKeys = ParseFloatList(keyMatch.Groups[1].Value);

                    // Aggiungi al dizionario se abbiamo sia tempi che chiavi
                    if (currentName != "" && currentTimes != null && currentKeys != null)
                    {
                        motionTimes[currentName] = currentTimes;
                        motionKeys[currentName] = currentKeys;
                    }
                    continue;
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error reading the file: {ex.Message}");
        }

        return (motionKeys, motionTimes); // Restituisce i dizionari
    }

    // Funzione per convertire una stringa in una lista di float
    private static List<float> ParseFloatList(string input)
    {
        List<float> result = new List<float>();
        string[] parts = input.Split(',');
        foreach (var part in parts)
        {
            if (float.TryParse(part.Trim(), out float value))
            {
                result.Add(value);
            }
        }
        return result;
    }
}