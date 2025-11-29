#!/bin/bash
APP_FILE=$1

if [ -z "$APP_FILE" ]; then
    echo "Uso: ./run_flask.sh app.py"
    exit 1
fi

echo "[INFO] Instalando dependências..."
sudo apt update -y
sudo apt install -y python3-pip

if [ -f requirements.txt ]; then
    pip3 install -r requirements.txt
fi

echo "[INFO] Executando app Flask..."
python3 $APP_FILE
