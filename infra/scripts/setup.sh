#!/bin/bash
# CropMind — One-command local setup
set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🌱 CropMind Local Setup${NC}"
echo "================================================"

# 1. Backend .env
if [ ! -f backend/.env ]; then
  cp backend/.env.example backend/.env
  echo -e "${GREEN}✅ Created backend/.env${NC}"
else
  echo "   backend/.env already exists"
fi

# 2. Start infra
echo -e "\n${CYAN}Starting PostgreSQL, Redis, Ollama...${NC}"
cd backend && docker-compose up -d && cd ..
sleep 5

# 3. Install Python deps
echo -e "\n${CYAN}Installing Python dependencies...${NC}"
cd backend
pip install -r requirements.txt --quiet
echo -e "${GREEN}✅ Python deps installed${NC}"

# 4. Run migrations
echo -e "\n${CYAN}Running database migrations...${NC}"
alembic upgrade head
echo -e "${GREEN}✅ Database ready${NC}"
cd ..

# 5. Pull Ollama model
echo -e "\n${CYAN}Pulling Mistral 7B (this may take a few minutes)...${NC}"
docker exec cropmind_ollama ollama pull mistral:7b-instruct-q4_K_M
echo -e "${GREEN}✅ LLM ready${NC}"

# 6. Mobile deps
echo -e "\n${CYAN}Installing mobile dependencies...${NC}"
cd mobile && npm install --silent && cd ..
echo -e "${GREEN}✅ Mobile deps installed${NC}"

echo ""
echo -e "${GREEN}================================================"
echo -e "🚀 CropMind is ready!"
echo -e "================================================${NC}"
echo ""
echo "  Start backend:  cd backend && uvicorn app.main:app --reload"
echo "  API docs:       http://localhost:8000/docs"
echo "  Start mobile:   cd mobile && npx expo start"
echo ""
echo "  Train ML model: python ml/training/train_mobilenet.py --data_dir ./ml/datasets/plantvillage"
echo ""
