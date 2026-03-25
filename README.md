# 🎙️ VoiceOS — AI Voice Assistant for Windows

> Control your entire Windows PC with your voice. 100% free. 100% offline. No API costs ever.

![VoiceOS](https://img.shields.io/badge/VoiceOS-v1.0-7c4dff?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![React](https://img.shields.io/badge/React-18-61dafb?style=for-the-badge&logo=react)
![Electron](https://img.shields.io/badge/Electron-Desktop-47848f?style=for-the-badge&logo=electron)
![Ollama](https://img.shields.io/badge/Ollama-LLaMA3-orange?style=for-the-badge)

---

## 📖 What is VoiceOS?

VoiceOS is a native Windows desktop application that lets you control your PC using voice commands or text input. It has two main sections:

- **🎙️ AI Voice Assistant** — Speak or type commands like "open chrome", "search youtube for lofi music", "send email to john@gmail.com about meeting saying see you at 3pm" and VoiceOS executes them automatically.
- **🛡️ Permission Manager** — A dashboard to view and control Windows startup apps, running processes, and system permissions.

### ✨ Key Features
- 100% offline — no internet needed after setup
- Zero API costs — runs on your own PC
- LLaMA3 AI brain understands natural language
- Whisper speech-to-text (works without internet)
- Multi-agent system with Redis message bus
- ChromaDB memory — remembers your past commands
- Professional dark UI built with React + Material UI
- Runs as a real Windows desktop app via Electron

---

## 🖥️ System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| OS | Windows 10 64-bit | Windows 11 64-bit |
| RAM | 8GB | 16GB |
| Disk Space | 15GB free | 20GB free |
| Microphone | Required for voice mode | Any USB or built-in mic |
| Internet | Only for first-time downloads | Not needed after setup |

---

## 📁 Project Structure

```
C:\VoiceOS\
├── backend\
│   ├── venv\                    # Python virtual environment
│   ├── main.py                  # FastAPI server (port 8000)
│   ├── voice_pipeline.py        # Whisper + microphone (Agent 3)
│   ├── intent_parser.py         # LLaMA3 AI brain
│   ├── executor.py              # Windows actions (Agent 5)
│   ├── permissions.py           # Windows permissions (Agent 4)
│   ├── agent_manager.py         # Orchestrator agent
│   ├── message_bus.py           # Redis inter-agent communication
│   ├── memory.py                # ChromaDB command memory (Agent 6)
│   ├── run_agents.py            # Starts all agents
│   └── voiceos.log              # Log file
├── frontend\
│   └── voiceos-ui\
│       ├── src\
│       │   └── App.js           # React UI
│       ├── electron.js          # Electron desktop wrapper
│       └── package.json
├── memory\                      # ChromaDB persistent storage
├── screenshots\                 # Voice command screenshots
└── startup.bat                  # Windows autostart script
```

---

## 🚀 Installation Guide

Follow every step exactly. Do not skip any step.

### Step 1 — Install Python 3.11

1. Download Python 3.11: https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
2. Run the installer
3. ⚠️ **IMPORTANT**: Check the box **"Add Python to PATH"** before clicking Install
4. Verify installation:

```bash
python --version
pip --version
```

Expected output: `Python 3.11.x`

---

### Step 2 — Install Node.js

1. Download Node.js LTS: https://nodejs.org/dist/v20.19.0/node-v20.19.0-x64.msi
2. Run installer with default settings
3. Verify:

```bash
node --version
npm --version
```

Expected output: `v20.x.x`

---

### Step 3 — Install Git

1. Download Git: https://github.com/git-for-windows/git/releases/download/v2.47.1.windows.1/Git-2.47.1-64-bit.exe
2. Run installer with default settings
3. Verify:

```bash
git --version
```

---

### Step 4 — Install VS Code

1. Download VS Code: https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-user
2. Install with default settings
3. Open VS Code and install these extensions (Ctrl+Shift+X):
   - Python (by Microsoft)
   - ESLint
   - Prettier

---

### Step 5 — Install ffmpeg

1. Download ffmpeg: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
2. Extract the zip
3. Rename the extracted folder to `ffmpeg`
4. Move it to `C:\ffmpeg`
5. Add to PATH:
   - Press **Win + S** → search "Environment Variables"
   - Click "Edit the system environment variables"
   - Click "Environment Variables"
   - Under "System variables" find **Path** → click Edit
   - Click New → type `C:\ffmpeg\bin`
   - Click OK on all windows
6. Open a new terminal and verify:

```bash
ffmpeg -version
```

---

### Step 6 — Install Ollama and LLaMA3

1. Download Ollama: https://ollama.com/download/OllamaSetup.exe
2. Run installer — Ollama starts as a background service automatically
3. Open terminal and verify:

```bash
ollama --version
```

4. Download LLaMA3 model (4.7GB — takes 10-30 minutes):

```bash
ollama pull llama3
ollama pull mistral
```

5. Test LLaMA3:

```bash
ollama run llama3
```

Type: `Say hello in one word` — it should reply with `Hello`

Type `/bye` to exit.

---

### Step 7 — Install Redis

1. Download Redis: https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.msi
2. Run installer with default settings
3. Open Command Prompt as Administrator and run:

```bash
redis-server --service-install
redis-server --service-start
redis-cli ping
```

Expected output: `PONG`

---

### Step 8 — Clone the Repository

```bash
git clone https://github.com/YOURUSERNAME/voiceos.git C:\VoiceOS
cd C:\VoiceOS
```

---

### Step 9 — Set Up Python Virtual Environment

```bash
cd C:\VoiceOS\backend
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` at the start of your terminal prompt.

---

### Step 10 — Install Python Dependencies

```bash
pip install fastapi uvicorn pyaudio openai-whisper
pip install pywin32 pyautogui psutil pyperclip
pip install redis chromadb
pip install requests python-dotenv scipy numpy
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

⚠️ The torch install is large (~800MB). Be patient.

Verify all packages:

```bash
python -c "import whisper; print('Whisper OK')"
python -c "import pyaudio; print('PyAudio OK')"
python -c "import fastapi; print('FastAPI OK')"
python -c "import redis; print('Redis OK')"
python -c "import chromadb; print('ChromaDB OK')"
```

Every line should print OK.

---

### Step 11 — Download Whisper Model

```bash
python -c "import whisper; whisper.load_model('small'); print('Whisper model ready')"
```

This downloads the small model (~460MB). Takes a few minutes.

---

### Step 12 — Install Node.js Dependencies

```bash
cd C:\VoiceOS\frontend\voiceos-ui
npm install
npm install electron electron-builder concurrently wait-on --save-dev
```

---

## ▶️ Running VoiceOS

You need **3 terminals** running at the same time.

### Terminal 1 — Start FastAPI Backend

```bash
cd C:\VoiceOS\backend
venv\Scripts\activate
python main.py
```

Wait until you see:
```
INFO: Uvicorn running on http://127.0.0.1:8000
```

---

### Terminal 2 — Start React UI

```bash
cd C:\VoiceOS\frontend\voiceos-ui
npm start
```

Wait until you see:
```
Compiled successfully!
```

---

### Terminal 3 — Start Electron Desktop App

```bash
cd C:\VoiceOS\frontend\voiceos-ui
.\node_modules\.bin\electron electron.js
```

VoiceOS desktop window will open automatically.

---

## 🎤 Voice Mode vs Text Mode

VoiceOS has two modes controlled by one line in `voice_pipeline.py`:

```python
MODE = 'text'   # Type commands in terminal — use this in VirtualBox
MODE = 'voice'  # Speak commands via microphone — use this on real Windows
```

### Switching to Voice Mode

1. Open `C:\VoiceOS\backend\voice_pipeline.py`
2. Change `MODE = 'text'` to `MODE = 'voice'`
3. Find your microphone index:

```bash
cd C:\VoiceOS\backend
venv\Scripts\activate
python find_mic.py
```

4. Update `MIC_INDEX` in `voice_pipeline.py` to match your microphone
5. Restart the backend

---

## 💬 Example Commands

| Command | What Happens |
|---------|--------------|
| `open chrome` | Opens Google Chrome |
| `open notepad` | Opens Notepad |
| `take a screenshot` | Saves screenshot to C:\VoiceOS\screenshots\ |
| `set volume to 50` | Sets system volume to 50% |
| `minimize all windows` | Minimizes all open windows |
| `open youtube` | Opens YouTube in browser |
| `search youtube for lofi music` | Searches YouTube for lofi music |
| `open gmail` | Opens Gmail in browser |
| `search google for python tutorials` | Google searches python tutorials |
| `open github` | Opens GitHub in browser |
| `ask chatgpt what is python` | Opens ChatGPT and types your question |
| `ask claude explain machine learning` | Opens Claude and types your question |
| `open notepad and type hello world` | Opens Notepad and types hello world |
| `send email to john@gmail.com about meeting saying see you at 3pm` | Opens Gmail and composes email |
| `create folder named projects` | Creates a folder on desktop |
| `close notepad` | Closes Notepad |
| `open calculator` | Opens Calculator |

---

## 🔧 Troubleshooting

### Whisper gives wrong transcription
- Speak slowly and clearly
- Make sure microphone volume is at 100% in Windows Sound Settings
- Try switching to `whisper.load_model('medium')` for better accuracy

### Ollama not responding
```bash
ollama serve
```

### Redis not found
```bash
"C:\Program Files\Redis\redis-server.exe" --service-start
"C:\Program Files\Redis\redis-cli.exe" ping
```

### PyAudio error / mic not detected
```bash
cd C:\VoiceOS\backend
venv\Scripts\activate
python find_mic.py
```

Update `MIC_INDEX` in `voice_pipeline.py` to the correct index.

### pywin32 errors
Open Command Prompt as Administrator:
```bash
cd C:\VoiceOS\backend
venv\Scripts\activate
python Scripts\pywin32_postinstall.py -install
```

### FastAPI not starting — module not found
Make sure venv is activated:
```bash
cd C:\VoiceOS\backend
venv\Scripts\activate
python main.py
```

### Chrome not opening
Check Chrome is installed at:
```
C:\Program Files\Google\Chrome\Application\chrome.exe
```

If installed elsewhere, update `APP_MAP` in `executor.py` with the correct path.

---

## 🏃 Quick Start (After Installation)

Once everything is installed, use this quick start every time:

```bash
# Terminal 1 — Backend
cd C:\VoiceOS\backend && venv\Scripts\activate && python main.py

# Terminal 2 — Frontend
cd C:\VoiceOS\frontend\voiceos-ui && npm start

# Terminal 3 — Desktop App
cd C:\VoiceOS\frontend\voiceos-ui && .\node_modules\.bin\electron electron.js
```

Or just double-click `C:\VoiceOS\startup.bat` to start the backend automatically.

---

## 🔄 Auto-Start with Windows

To make VoiceOS start automatically when Windows boots:

1. Press **Win + R**
2. Type `shell:startup`
3. Press Enter
4. Copy a shortcut to `C:\VoiceOS\startup.bat` into the folder that opens

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| AI Brain | Ollama + LLaMA3 (local) |
| Speech to Text | OpenAI Whisper (local) |
| Backend API | Python FastAPI |
| Message Bus | Redis pub/sub |
| Memory | ChromaDB vector database |
| Frontend | React + Material UI |
| Desktop App | Electron |
| Windows Control | pyautogui + pywin32 |

---

## 📝 License

MIT License — free to use, modify and distribute.

---

## 🙏 Credits

Built with:
- [Ollama](https://ollama.com) — local AI model runner
- [Whisper](https://github.com/openai/whisper) — speech recognition
- [FastAPI](https://fastapi.tiangolo.com) — Python web framework
- [Redis](https://redis.io) — message bus
- [ChromaDB](https://www.trychroma.com) — vector database
- [React](https://react.dev) — UI framework
- [Electron](https://www.electronjs.org) — desktop app framework

---

*Built in 30 days. 100% free. 100% offline. 100% yours.* 🚀
