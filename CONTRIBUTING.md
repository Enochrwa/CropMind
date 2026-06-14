# Contributing to CropMind

Thank you for helping feed the world! 🌱

## How to Contribute

### 1. Add a new language translation
Copy `mobile/src/i18n/translations/en.json` → `<lang_code>.json`
Translate all values. Open a PR with title: `feat(i18n): add <language> translation`

Currently needed: `ha` (Hausa), `am` (Amharic), `hi` (Hindi), `ar` (Arabic)

### 2. Add crop disease training images
- Upload labelled images to `ml/datasets/contributions/`
- Follow the naming convention: `<disease_key>_<number>.jpg`
- Minimum 50 images per new class

### 3. Add regional supplier data
Edit `infra/scripts/seed_suppliers.csv` with columns:
`name, phone, whatsapp, address, country, region, lat, lng, products`

### 4. Fix a bug
- Create a branch: `git checkout -b fix/<issue-number>-short-desc`
- Write a test that reproduces the bug
- Fix it, ensure tests pass: `cd backend && pytest`
- Open a PR

### 5. Add a new disease class
1. Add images to PlantVillage-format folder in `ml/datasets/`
2. Add entry to `backend/app/ml/disease_classes.py`
3. Retrain model using `ml/training/train_mobilenet.py`
4. Export new TFLite and commit to `ml/exports/`

## Code Standards

- Python: `ruff` for linting, type hints everywhere, docstrings on all public functions
- TypeScript: `eslint` + `@typescript-eslint`, no `any` types
- Commits: Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`)
- Tests required for all new backend endpoints

## Local Development

```bash
# Backend
cd backend
cp .env.example .env
docker-compose up -d postgres redis ollama
pip install -r requirements.txt
alembic upgrade head
ollama pull mistral:7b-instruct-q4_K_M
uvicorn app.main:app --reload
# API docs: http://localhost:8000/docs

# Mobile
cd mobile
npm install
npx expo start
# Scan QR with Expo Go app
```

## Community

- Issues: GitHub Issues
- Discussions: GitHub Discussions
- Urgent: Open an issue with label `urgent`

All contributors are listed in [CONTRIBUTORS.md](CONTRIBUTORS.md).
