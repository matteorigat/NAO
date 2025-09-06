# NAO – Social Presence and Emotional Interaction

This repository contains the code, results, and experimental framework developed for the master thesis:

**“Social Presence and Emotional Interaction: Comparing NAO Robot and its Digital Twin”**  
Master Thesis by *Matteo Rigat* (University of Milan, A.Y. 2024–2025)

---

![Physical vs Virtual NAO](/img/real_vs_virtual.png)

---

## 📑 Thesis Document
The full methodology, experimental setup, and analysis can be found in the master thesis: 📄 [Download the full thesis PDF](./Thesis_Rigat_Matteo_PDF_A.pdf)

---

## 📖 Overview

The project investigates whether a **virtual twin of the NAO humanoid robot** can effectively replace the physical robot in Human-Robot Interaction (HRI) experiments, with a focus on **emotion recognition** and **empathetic dialogue**.

Key contributions:
- Development of a **high-fidelity digital twin** of NAO in Unity, synchronized with the physical robot.
- Implementation of **12 emotional gestures** (happiness, sadness, anger, fear), grounded in HRI literature.
- Comparative user study with **24 participants**, showing no significant difference in emotion recognition between physical and virtual robots.
- Extension of the platform with an **empathetic Large Language Model (LLM)** for real-time dialogue.

---

## 📂 Repository Structure

A large amount of additional code used for testing, result calculations, and experiments has been omitted here. 
Only the essential code to run the two NAO robots (real and Unity) is included.

```
NAO-Project/
├── Choregraphe/                  # Choregraphe project with emotion gestures; just import into Choregraphe
│
├── NAO-2.7/
│   ├── Gestures_new/             # Folder containing emotion gestures exported from Choregraphe
│   │   └── ...
│   ├── objective 0/
│   │   └── main-ob0.py           # Main for Objective 0
│   └── objective 1/
│       └── main-ob1.py           # Main for Objective 1
│
├── NAO-LLM/
│   ├── main.py                   # Main for Objective 1 to control the real NAO → transcripts saved in objective 1/results_real/  
│   ├── main-unity.py             # Main for Objective 1 to control the Unity NAO → transcripts saved in objective 1/results_virtual/ 
│   ├── serverLLM.py              # Contains a lot of functions imported into the main scripts
│   ├── objective 0/
│   │   ├── main-ob0.py           # Main for Objective 0 to control both the real and Unity NAO and launch the web questionnaire
│   │   └── results/              # Feedback Objective 0
│   └── objective 1/
│       ├── results_real/         # Feedback Objective 1
│       └── results_virtual/      # Feedback Objective 1
│
└── NAO-UNITY/
    └── Scripts
        ├── EyeLEDController.cs   # Script to animate the Unity NAO’s eyes
        ├── Gestures_new/         # Folder containing emotion gestures exported from Choregraphe
        ├── MotionExtractor.cs    # Extracts keys and times
        ├── NaoMovements.cs       # Calculates movements from extracted keys and times
        └── SocketServer.cs       # Main script that communicates with NAO-LLM/main-unity.py
```

--- 

## 🚀 How to Run

1. **Objective 0**
   - Turn on the real NAO
   - Run Unity project
   - Run `NAO-2.7/objective 0/main-ob0.py`
   - Run `NAO-LLM/objective 0/main-ob0.py`

2. **Objective 1**
   - **Real NAO**
     - Turn on the real NAO
     - Run `NAO-2.7/objective 1/main-ob1.py`
     - Run `NAO-LLM/main.py`

   - **Unity NAO**
     - Run Unity project
     - Run `NAO-LLM/main-unity.py`

