# 🤖 Windows AI Assistant — Local, Private, Aware

> A production-grade AI assistant with real-time desktop awareness, audio monitoring, and MCP integration — **100% offline, no cloud, no telemetry**.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Windows LSTC](https://img.shields.io/badge/platform-Windows%20LSTC-brightgreen)](.)

**Windows AI Assistant** sees your screen, hears your environment, and automates tasks — all while respecting your privacy.

---

## ✨ Key Features

| Feature | Description | Privacy Benefit |
|---------|-------------|----------------|
| 🖥️ **Desktop Awareness** | Real-time 4K screen capture → 1080p processing, motion detection, window tracking | No screenshots leave your machine |
| 🔊 **Audio Awareness** | Microphone monitoring, loud noise detection, silence alerts | Audio processed locally, never uploaded |
| 🛡️ **Emergency Brake** | Ctrl+Alt+Shift+E (double-tap) freezes all automation instantly | You always retain control |
| 🔌 **MCP Integration** | 64 WinScript tools for UI automation via Model Context Protocol | Extensible without cloud APIs |
| 🧠 **Local LLM** | Ollama (gemma3:4b) for event analysis and reasoning | No prompts sent to external servers |

---

## 🚀 Quick Start

```powershell
# 1. Clone
git clone https://github.com/ismailwiess4-creator/windows-ai-assistant
cd windows-ai-assistant

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start Ollama (if not running)
ollama serve
ollama pull gemma3:4b

# 4. Run the assistant
python -m src.windows_ai.assistant

# 5. Try a command
> "Open Notepad and write a short note"
```

**Expected output:**
```
✅ Emergency brake active (Ctrl+Alt+Shift+E to freeze)
✅ Desktop awareness: 10 FPS, 1080p processing
✅ Audio awareness: listening on default device
✅ MCP connected: 64 tools available
✅ LLM ready: gemma3:4b @ http://localhost:11434

> Open Notepad and write a short note
🤖 [WinScript] open_app("notepad")
🤖 [WinScript] type_text("Hello from Windows AI Assistant!")
✅ Task completed.
```

---

## 🧠 Architecture

```
┌─────────────────┐
│   USER INPUT    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SAFETY LAYER   │ ← Emergency Brake (Ctrl+Alt+Shift+E)
└────────┬────────┘
         │
   ┌─────┴─────┐
   ▼           ▼
┌───────┐ ┌─────────┐
│Desktop│ │ Audio   │
│Aware- │ │Aware-  │
│ness   │ │ness    │
└───┬───┘ └────┬────┘
    │          │
    └────┬─────┘
         ▼
┌─────────────────┐
│   MCP LAYER     │ ← WinScript (64 tools)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   LLM LAYER     │ ← Ollama (gemma3:4b, local)
└─────────────────┘
```

**All processing happens on your machine. No data leaves your computer.**

---

## 🔧 Configuration

Edit `src/windows_ai/config.yaml`:

```yaml
desktop_awareness:
  capture_fps: 10          # Frames per second (lower = less CPU)
  motion_threshold: 0.03   # 3% pixel change triggers motion event
  ignore_regions:          # Prevent false positives
    - [0, 2100, 3840, 2160]  # Ignore taskbar (x1,y1,x2,y2)

audio_awareness:
  threshold_db: 60.0       # Loud noise detection threshold
  silence_timeout: 300     # Alert after 5 minutes of silence

ollama:
  model: gemma3:4b
  timeout: 30
  temperature: 0.1         # Lower = more deterministic
```

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'cv2'` | Run `pip install opencv-python` |
| `Ollama connection refused` | Ensure `ollama serve` is running; check `http://localhost:11434` |
| `Audio device not found` | Run `python -m src.windows_ai.audio_awareness --list-devices` to see available inputs |
| `High CPU usage` | Lower `capture_fps` in `config.yaml` to 5; enable GPU acceleration in OpenCV |
| `Emergency brake not responding` | Ensure `keyboard` module has admin privileges on Windows |

**Still stuck?** Open an issue at [github.com/ismailwiess4-creator/windows-ai-assistant/issues](https://github.com/ismailwiess4-creator/windows-ai-assistant/issues)

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- How to report bugs or suggest features
- Coding standards and testing guidelines
- Ways to help (code, docs, translations, ideas)

---

## 📜 License

MIT License — Use, modify, distribute freely. Credit appreciated.

> *"Technology should protect the vulnerable, not profile them."*

---

## 👤 Built by

**Ismail Wiess** — engineer, seeker of dignity.  
📍 Belgium | 🌍 Multipolar, privacy-first, open-source

*Inspired by a mother's last prayer: "God help and bless me and make my project work."*

---

## 🙏 Acknowledgments

- The open-source community for the tools that make this possible
- WinScript MCP maintainers for Windows automation primitives
- Ollama team for local LLM accessibility
- You, for caring about privacy and local AI

*If this project helps you, pay it forward: help someone else.*
