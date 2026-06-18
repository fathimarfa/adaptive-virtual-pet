# 🐾 Adaptive Virtual Pet Companion

A full-stack AI-powered virtual pet web app that reads your facial emotions in real time and responds with adaptive, personality-driven conversation.

---

## ✨ Features

- 🎭 **Real-time emotion detection** — webcam detects your facial expression every 10 seconds using DeepFace + OpenCV
- 🤖 **LLM-powered dialogue** — pet responds naturally using Groq API (LLaMA 3.1-8b), adapting to your mood and its own state
- 🧠 **Finite State Machine** — pet has 6 states (idle, happy, sad, hungry, sleepy, excited) that transition based on your emotions and activities
- 📈 **XP + levelling system** — pet matures across 5 levels, speech evolves from baby talk to eloquent conversation
- 🍖 **Activity buttons** — Feed, Play, Rest directly affect pet stats and FSM state
- 📊 **Stat decay** — hunger and energy decay over time; pet asks for food/rest when critical
- 🎤 **Voice interaction** — browser-native TTS (pet speaks) and STT (you speak) via Web Speech API
- 🔐 **Face recognition login** — register and login with your face using DeepFace; PIN fallback included
- 💾 **Persistent memory** — pet remembers past conversations across sessions via SQLite
- 🎨 **Dual themes** — Dark/purple (Normal) and warm Cozy (beige/peach) theme, switchable anytime

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask, Flask-Blueprints, Flask-SocketIO |
| ORM / Database | SQLAlchemy, SQLite |
| AI / ML | DeepFace, OpenCV, Groq API (LLaMA 3.1-8b) |
| Pet Behaviour | Finite State Machine (`transitions` library) |
| Voice | Web Speech API (TTS + STT, browser-native) |
| Frontend | HTML, CSS (custom properties), Vanilla JS |
| Auth | DeepFace face verification, Werkzeug password hashing |

---

## 🚀 Running Locally

**1. Clone the repo**
```bash
git clone https://github.com/fathimarfa/adaptive-virtual-pet.git
cd adaptive-virtual-pet
```

**2. Create and activate virtual environment**
```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
pip install tf-keras
```

**4. Create `.env` file**
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///virtual_pet.db
LLM_API_KEY=your-groq-api-key
LLM_MODEL=llama-3.1-8b-instant
LLM_PROVIDER=groq

**5. Run**
```bash
python run.py
```

Visit `http://127.0.0.1:5000` — register with your face, then meet your pet.

---

## 📁 Project Structure
virtual-pet/
├── app/
│   ├── auth/          # Face login, PIN fallback, registration
│   ├── pet/           # FSM, LLM, routes, emotion detection
│   ├── static/        # CSS, JS
│   ├── templates/     # Jinja2 HTML templates
│   ├── models.py      # SQLAlchemy models (User, Pet, ChatHistory)
│   └── init.py    # App factory
├── config.py          # Environment-based configuration
├── run.py             # Entry point
├── requirements.txt
└── tests/
└── test_fsm.py

---

## 🧩 How It Works

1. User registers with a face photo + optional PIN
2. On login, DeepFace matches webcam frame against stored face
3. Pet page loads — webcam scans face every 10s, maps emotion to FSM trigger
4. FSM transitions pet state (e.g. you look happy → pet gets excited)
5. User types or speaks → message + current emotion sent to Groq LLM
6. LLM responds as the pet, aware of its own state, your emotion, and past memory
7. Response is spoken aloud via TTS, displayed in chat, pet sprite animates

---

## 🔮 Future Improvements

- Custom 2D character art replacing CSS emoji sprites
- WebSocket real-time emotion streaming instead of polling
- Mobile-responsive layout
- Docker deployment
- Personality customisation per user

---

Built with 🐾 by [Fathima Arfa](https://github.com/fathimarfa)