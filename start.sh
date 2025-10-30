#!/bin/bash

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Creating .env file if it doesn't exist..."
if [ ! -f .env ]; then
    cp .env.example .env
fi

echo "Starting the application..."
python run.py