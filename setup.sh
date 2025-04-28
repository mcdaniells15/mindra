#!/bin/bash

echo "Starting Mindra Setup..."

# 1. Start PostgreSQL in Docker
echo " Launching PostgreSQL container..."
docker run -d \
  --name mindra-postgres \
  -e POSTGRES_USER=mindra \
  -e POSTGRES_PASSWORD=devpass \
  -e POSTGRES_DB=mindra \
  -p 5432:5432 \
  postgres:15

# 2. Install backend dependencies
echo "Installing backend packages..."
cd backend
npm install

# 3. Set up Python venv and install ML requirements
echo "Setting up ML virtual environment..."
cd ml
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ../..

# 4. Install frontend packages
echo "Installing frontend packages..."
cd frontend
npm install
cd ..

echo "Mindra dev environment is ready!"
