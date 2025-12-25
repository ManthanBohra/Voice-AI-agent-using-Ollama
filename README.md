# 🎙️ Real-Time Voice AI Assistant (Local LLM Powered)

Build your own **JARVIS-like voice assistant** using Python that listens to you, thinks using a **local Llama 3 model**, and speaks back in real time — **no cloud inference required**.

This project demonstrates how modern AI systems can replicate human sensory loops using simple, modular components.

---

## ✨ Features

* 🎧 **Speech-to-Text (Ears)** — Converts your voice into text
* 🧠 **Local AI Reasoning (Brain)** — Uses **Llama 3 via Ollama** for intelligent responses
* 🔊 **Text-to-Speech (Mouth)** — Speaks responses naturally
* 🔒 **Privacy-First** — All AI inference runs locally
* 🔁 **Always-On Loop** — Continuous Listen → Think → Speak cycle
* ❌ **Graceful Exit** — Say *exit*, *stop*, or *quit* to shut down

---

## 🧠 How It Works

The assistant mimics three biological functions:

```
🎙️ Microphone
   ↓
Speech-to-Text (SpeechRecognition)
   ↓
LLM Reasoning (Llama 3 via Ollama)
   ↓
Text-to-Speech (pyttsx3)
   ↓
🔊 Speaker
```

Each interaction runs through this loop in real time.

---

## 🛠️ Tech Stack

* **Python 3.9+**
* **SpeechRecognition** — Voice input
* **PyAudio** — Microphone access
* **Ollama** — Local LLM runtime
* **Llama 3** — Large Language Model
* **pyttsx3** — Offline Text-to-Speech

---

## 📦 Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/voice-ai-assistant.git
cd voice-ai-assistant
```

### 2️⃣ Create & Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install speechrecognition ollama pyttsx3 pyaudio
```

> ⚠️ **PyAudio Installation Notes**

* macOS:

```bash
brew install portaudio
pip install pyaudio
```

* Windows: Install PyAudio wheel matching your Python version

---

## 🧠 Ollama Setup (Required)

1. Install Ollama:
   👉 [https://ollama.com](https://ollama.com)

2. Pull the Llama 3 model:

```bash
ollama pull llama3
```

3. Make sure Ollama is running in the background.

---

## ▶️ Usage

Run the assistant:

```bash
python main.py
```

You’ll hear:

> *“Hello, I am ready. You can start speaking.”*

Speak naturally — the assistant will listen, think, and respond.

### 🛑 Exit Command

Say:

* `exit`
* `stop`
* `quit`

---

## 🚀 Future Improvements

* 🔁 Streaming responses (real-time speech output)
* 🗓️ Calendar / Email / Task integrations
* 🧠 Memory using vector databases
* 🤖 Wake-word detection
* 🌐 Replace Google STT with fully offline alternatives
* 🖥️ GUI or desktop tray app

---

## 🔐 Privacy Note

* Voice recognition uses **Google Web Speech API** (requires internet)
* **LLM inference is 100% local**
* No prompts are sent to cloud AI providers

---

## 🤝 Contributing

Contributions, ideas, and improvements are welcome!

1. Fork the repo
2. Create a feature branch
3. Commit your changes
4. Open a Pull Request

---

## 📜 License

MIT License — free to use, modify, and distribute.

---

## ⭐ Final Thoughts

What once required massive infrastructure is now possible on a laptop.

This project is not just a chatbot — it’s a **foundation for autonomous AI agents**.

**JARVIS isn’t coming. We’re building it.** 🚀
