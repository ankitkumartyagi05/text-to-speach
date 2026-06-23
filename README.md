# 🎙️ Text To Speech App

🌐 **GitHub** → [🐙 Visit Profile](https://github.com/ankitkumartyagi05)

📊 **Kaggle** → [🏆 View Competitions & Notebooks](https://www.kaggle.com/ankitkumartyagiuset)

💼 **LinkedIn** → [👔 Connect Professionally](https://www.linkedin.com/in/ankit-kumar-tyagi-)


### 🔊 Convert Text Into Natural Human Speech Instantly

Fast • Lightweight • Browser-Based • Vercel Ready

---

# 🌐 Live Demo

### 🚀 Try It Now

🌐 **Live Demo:** 🚀 [Open Text To Speech App](https://text-to-speach-rho.vercel.app/) 🎙️🔊

---

# ✨ Features

## 🎤 Speech Generation

* 📝 Convert text to speech instantly
* 🌍 Multi-language support
* 🎧 High-quality MP3 output
* ⚡ Fast generation speed

---

## 📥 Download Support

* 💾 Download generated audio
* 📂 Custom file names
* 🎵 MP3 format support

---

## 🛡 Security & Stability

* 🔒 Session-based protection
* 🚫 Abuse prevention
* ⏳ Request limits
* ⚙️ Backend validation

---

## ☁️ Deployment Ready

* 🚀 Vercel compatible
* 📦 Lightweight setup
* 🔄 Serverless deployment
* ⚡ Fast startup

---

# 🧰 Tech Stack

| Technology   | Purpose           |
| ------------ | ----------------- |
| 🐍 Python    | Backend Logic     |
| 🌶 Flask     | Web Framework     |
| 🎤 gTTS      | Speech Generation |
| 🎨 HTML/CSS  | User Interface    |
| ⚡ JavaScript | Frontend Logic    |
| ☁️ Vercel    | Deployment        |

---

# 🚀 Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/text-to-speech-app.git
cd text-to-speech-app
```

## 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Run Locally

```bash
python app.py
```

Application will start on:

```text
http://localhost:5000
```

---

# 🖥️ How To Use

### Step 1

📝 Enter or paste your text

### Step 2

📄 Provide a file name

### Step 3

🌍 Select language (if available)

### Step 4

🎙 Click Generate Audio

### Step 5

🎧 Listen online or download MP3

---

# 🔄 Application Workflow

```text
User Input
     │
     ▼
Frontend UI
     │
     ▼
Flask Backend
     │
     ▼
Validation Layer
     │
     ▼
gTTS Engine
     │
     ▼
MP3 Generation
     │
     ▼
Audio Response
     │
     ▼
Download / Playback
```

---

# 🔌 API Endpoints

## 🏠 Home Page

```http
GET /
```

Returns the main application interface.

---

## 📊 Session Status

```http
GET /session-status
```

Returns:

```json
{
  "remaining_generations": 5,
  "session_active": true
}
```

---

## 🎙 Generate Audio

```http
POST /generate-audio
```

### Request

```json
{
  "text": "Hello world",
  "filename": "hello-world",
  "language": "en"
}
```

### Response

```json
{
  "success": true,
  "audio_url": "generated-audio.mp3"
}
```

---

# ☁️ Deployment

## Vercel Configuration

Project Structure:

```text
api/index.py
```

Acts as:

```text
Serverless Python Entry Point
```

---

## Deployment Flow

```text
GitHub Push
      │
      ▼
Vercel Build
      │
      ▼
Python Function
      │
      ▼
Production Deployment
```

---

# 📁 Project Structure

```text
text-to-speech-app/

├── app.py
│
├── api/
│   └── index.py
│
├── templates/
│   ├── index.html
│   ├── scripts.js
│   └── style.css
│
├── generated_audio/
│
├── requirements.txt
│
├── vercel.json
│
└── README.md
```

---

# 📈 Future Improvements

* 🎙 Multiple Voice Types
* 🌍 More Language Support
* 🤖 AI Voice Cloning
* 🎚 Speech Controls
* ☁️ Cloud Storage
* 📱 Mobile App

---

# 🛡 Limitations

* Maximum text length enforced
* Session limits enabled
* Temporary audio storage
* Depends on gTTS service availability

---

# 🤝 Contributing

Contributions are welcome.

```bash
Fork
│
├── Create Branch
├── Make Changes
├── Commit
├── Push
└── Open Pull Request
```

---

# ⭐ Support

If you found this project useful:

⭐ Star the repository

🍴 Fork the project

📢 Share with others

---

# 📄 License

Copyright © 2026

**Text To Speech App**

All Rights Reserved.

---

### 🎤 Transform Text Into Natural Speech Effortlessly

Made with ❤️ using Python, Flask & gTTS
