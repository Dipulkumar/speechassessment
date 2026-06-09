# 🎤 Speech Assessment System

An AI-powered **Speech Assessment System** that evaluates **pronunciation, speech quality, speech transcription, language detection, and speaker identification** using **Whisper AI**, **SpeechBrain**, and Speech Processing technologies.

---

## 📌 Project Overview

The **Speech Assessment System** is designed to analyze audio speech and provide intelligent feedback through AI-powered processing.

This system supports:

✅ Speech-to-Text Conversion
✅ Pronunciation Assessment
✅ Speaker Identification
✅ Language Detection
✅ Audio Processing
✅ Translation Support

The project integrates **Java Spring Boot** with **Python Flask AI services** for scalable and efficient speech analysis.

---

## 🚀 Features

* 🎙️ Upload Audio Files
* 📝 Speech Transcription using Whisper AI
* 🗣️ Pronunciation Analysis
* 👤 Speaker Identification
* 🌍 Language Detection & Translation
* 🔊 Audio Processing
* ⚡ REST API Integration
* 🔄 Communication between Spring Boot & Flask Services

---

## 🛠️ Technologies Used

### Backend

* Java
* Spring Boot
* Maven
* REST APIs

### AI / Speech Processing

* Python
* Flask
* Whisper AI
* SpeechBrain
* Transformers

### Frontend

* HTML
* CSS
* JavaScript

### Database

* MySQL / H2 Database

### Tools

* Git
* GitHub
* Postman
* VS Code
* IntelliJ IDEA / Eclipse

---

## 🏗️ System Architecture

```text
                User Upload Audio
                        │
                        ▼
              Spring Boot Backend
                        │
                        ▼
                Flask AI Service
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
     Whisper AI   SpeechBrain   Language Detection
         │              │
         └──────────────┼──────────────┘
                        ▼
             Speech Assessment Result
                        │
                        ▼
                   Result Display
```

---

## 📂 Project Structure

```text
Project/
├── speechassessment/      # Spring Boot Application
├── whisper-services/      # Python AI Services
├── sampleAudio/           # Sample audio files
├── screenshots/           # Project screenshots
└── README.md
```

---

## 📸 Screenshots

### 🏠 Home Page

![Home Page](home%20page.png)

### 🎙️ Speech to Text

![Speech to Text](speechtotext.png)

### 🌍 Language Detection

![Language Detection](Language%20Detection.png)

> Place screenshot images in the root folder or use a dedicated `screenshots` folder.

---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/Dipulkumar/speechassessment.git
cd speechassessment
```

---

## ☕ Run Spring Boot Application

### Requirements

* Java 17+
* Maven

### Run Command

```bash
mvn spring-boot:run
```

Application runs at:

```text
http://localhost:8080
```

---

## 🐍 Run Python AI Service

### Requirements

* Python 3.10+

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Flask Service

```bash
python app.py
```

Flask service runs at:

```text
http://localhost:5000
```

---

## 🔌 API Endpoints

| Endpoint      | Method | Description              |
| ------------- | ------ | ------------------------ |
| `/transcribe` | POST   | Convert speech to text   |
| `/assess`     | POST   | Pronunciation assessment |
| `/speaker`    | POST   | Speaker identification   |
| `/translate`  | POST   | Speech translation       |

---

## 🧪 API Testing

You can test APIs using:

* Postman
* Swagger
* Browser API Tools

Example Request:

```http
POST /transcribe
Content-Type: multipart/form-data
```

Upload an audio file for speech transcription.

---

## 📈 Future Improvements

* User Authentication
* Real-time Speech Analysis
* Improved Pronunciation Scoring
* Dashboard Analytics
* Cloud Deployment
* AI Accuracy Optimization

---

## 🎯 Learning Outcomes

Through this project, I gained hands-on experience in:

* Spring Boot Development
* REST API Development
* Flask Microservices
* Whisper AI Integration
* SpeechBrain Integration
* Speech Processing
* Backend Communication
* Audio Analysis

---

## 👨‍💻 Author

**Dipul Kumar**

GitHub:
https://github.com/Dipulkumar

LinkedIn:
linkedin.com/in/dipulkumar07

---


