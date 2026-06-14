<div align="center">

# 🌱 CropMind

**Point. Diagnose. Save your harvest.**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React Native](https://img.shields.io/badge/React%20Native-0.74-61DAFB?logo=react)](https://reactnative.dev)
[![TFLite](https://img.shields.io/badge/TensorFlow%20Lite-2.16-FF6F00?logo=tensorflow)](https://www.tensorflow.org/lite)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

*The crop disease diagnostic platform for 500 million smallholder farmers — offline-first, 8 MB, works on a $60 Android.*

[Docs](docs/) · [API Reference](docs/api/) · [Architecture](docs/architecture/) · [Contributing](CONTRIBUTING.md)

</div>

---

## 🎯 What is CropMind?

CropMind is a mobile-first, AI-powered crop disease diagnostic platform built for smallholder farmers worldwide. A farmer takes a photo of a diseased plant, gets an **instant offline diagnosis** in their language, and receives:

- ✅ Disease / pest / deficiency identification (on-device, no internet needed)
- ✅ Step-by-step treatment plan in their local language
- ✅ Nearest verified local supplier with current stock
- ✅ Current market price for their crop in their region
- ✅ Voice Q&A with an AI agronomist
- ✅ Farm history tracking + recurring pattern alerts

**Monetisation:** Balance-based micro-payments (top up from 500 RWF / ~$0.40). Each enriched diagnosis costs ~600 RWF. The on-device detection is always free.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    MOBILE APP (Expo)                     │
│  • React Native + Expo SDK 51                           │
│  • TFLite on-device model (2 MB) — offline detection    │
│  • Expo SQLite — 90-day local farm history              │
│  • Whisper voice input                                  │
│  • i18n: EN, FR, SW, KIN, HA, AM, PT (extensible)      │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS (when online)
┌────────────────────▼────────────────────────────────────┐
│                  BACKEND (FastAPI)                       │
│  • /api/v1/diagnose  — enrichment layer                 │
│  • /api/v1/suppliers — regional supplier lookup         │
│  • /api/v1/prices    — crop market prices               │
│  • /api/v1/chat      — AI agronomist Q&A               │
│  • /api/v1/balance   — top-up + deduction               │
│  • /api/v1/outbreaks — disease heatmap (B2B)            │
│  Celery + Redis for async tasks                         │
│  PostgreSQL + PostGIS for spatial queries               │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                   AI / ML LAYER                         │
│  • MobileNetV3 fine-tuned (PlantVillage 54K images)    │
│  • Exported to TFLite (on-device) + ONNX (server)      │
│  • Mistral 7B via Ollama (agri fine-tuned LoRA)         │
│  • Whisper-small for voice transcription                │
│  • Helsinki-NLP OPUS for translation                    │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker + Docker Compose
- Expo CLI (`npm install -g expo-cli`)

### 1. Clone & configure
```bash
git clone https://github.com/Enochrwa/CropMind.git
cd CropMind
cp backend/.env.example backend/.env
# Edit backend/.env with your settings
```

### 2. Start the backend
```bash
cd backend
docker-compose up -d        # starts postgres, redis, ollama
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### 3. Pull the AI model
```bash
# Ollama must be running (started by docker-compose)
ollama pull mistral:7b-instruct-q4_K_M
```

### 4. Start the mobile app
```bash
cd mobile
npm install
npx expo start
```

---

## 📁 Project Structure

```
CropMind/
├── backend/                 # FastAPI server
│   ├── app/
│   │   ├── api/v1/          # REST endpoints
│   │   ├── core/            # Config, security, logging
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   ├── ml/              # Model inference wrappers
│   │   ├── tasks/           # Celery async tasks
│   │   └── db/              # DB session, migrations
│   ├── tests/
│   ├── alembic/
│   ├── requirements.txt
│   └── docker-compose.yml
│
├── mobile/                  # React Native (Expo)
│   ├── src/
│   │   ├── screens/         # Camera, Results, History, etc.
│   │   ├── components/      # Reusable UI components
│   │   ├── hooks/           # Custom hooks
│   │   ├── services/        # API client, offline queue
│   │   ├── store/           # Zustand global state
│   │   ├── i18n/            # Translations (7 languages)
│   │   └── utils/
│   ├── app.json
│   └── package.json
│
├── ml/                      # Model training
│   ├── training/            # Training scripts
│   ├── notebooks/           # Colab-ready notebooks
│   ├── datasets/            # Dataset download scripts
│   └── exports/             # Exported TFLite / ONNX models
│
├── infra/                   # Infrastructure as code
│   ├── docker/
│   ├── nginx/
│   └── scripts/
│
├── docs/                    # Documentation
├── .github/workflows/       # CI/CD
└── docker-compose.yml       # Root compose (full stack)
```

---

## 🌍 Supported Languages

| Language | Code | Status |
|---|---|---|
| English | `en` | ✅ Complete |
| French | `fr` | ✅ Complete |
| Kinyarwanda | `kin` | ✅ Complete |
| Swahili | `sw` | ✅ Complete |
| Hausa | `ha` | 🔄 In progress |
| Amharic | `am` | 🔄 In progress |
| Portuguese (BR) | `pt` | ✅ Complete |

---

## 💰 Business Model

| Revenue Stream | Unit Price | Who Pays |
|---|---|---|
| Enriched diagnosis | 600 RWF (~$0.50) | Farmer |
| Supplier listing (verified) | $50/mo per listing | Agro-input companies |
| Outbreak heatmap API | $500/mo | Govts, ministries |
| Farmer enrollment (NGO API) | $2 per farmer | NGOs, development orgs |
| Crop insurance verification | $1 per claim | Insurance companies |

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). All contributions welcome — especially:
- New language translations
- Regional supplier data
- Crop disease training images
- Local market price integrations

---

## 📄 License

MIT — see [LICENSE](LICENSE)

---

<div align="center">
Built for the 500 million farmers who feed the world. 🌍
</div>
