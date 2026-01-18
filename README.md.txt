# 🚨 Disaster Triage AI (Text + Image)

A Streamlit-based **Disaster Triage System** that analyzes **distress text messages** and **disaster images (flood scenes)** to determine emergency **priority**, classify the **incident category**, and provide **serious safety suggestions**.

---

## 📌 Project Overview
During disasters (especially floods), emergency teams receive a high volume of information. This system helps by providing quick triage.

✅ Accepts:
- Distress **text messages**
- Disaster **images** (flood/water level scenes)

✅ Produces:
- **Final Priority:** High / Medium / Low  
- **Category:** Rescue / Medical / Logistics / General  
- **Flood Severity (Image-based):** Low / Moderate / Severe  
- **Water Coverage % (Image-based estimation)**
- **Emergency suggestions**:
  - ⚡ Immediate Actions  
  - 🚫 What NOT to do  
  - 🧰 Preparedness Checklist

---

## 🎯 Problem Statement
In emergency situations, manual triage of incoming distress messages and images can delay response time and increase risk.

This project aims to:
- classify urgency and category quickly
- estimate flood severity from images
- provide actionable safety guidance

---

## ✅ Key Features

### 1) Text-based Triage
- Keyword-based classification:
  - Medical / Rescue / Logistics / General  
- Priority prediction: High / Medium / Low

### 2) Image-based Flood Analysis (FREE, Offline)
Flood severity is estimated using OpenCV heuristics:
- **Water coverage percentage**
- **Low visibility detection (night/dark scenes)**
- **Fire-like region detection**
- **Debris / clutter risk detection**

✅ No paid APIs, no API keys.

### 3) Serious Safety Suggestions
Suggestions are generated based on combined text + image risk signals:
- strict emergency actions
- important safety “don’ts”
- evacuation-ready checklist

### 4) User-controlled Image Display
- Image preview with **user-adjustable width slider**
- Image metadata shown:
  - Dimensions (W × H)
  - File size (KB/MB)

---

## 🧠 Tech Stack
- **Python**
- **Streamlit**
- **OpenCV**
- **Pillow (PIL)**
- **NumPy**

---

## 📂 Project Structure
```text
disaster-triage-ai/
│── README.md
│── requirements.txt
│── src/
    │── app.py
    │── engine.py
