#!/bin/bash

# スクリプトのあるディレクトリに移動
cd "$(dirname "$0")"

echo "=== AsahiBot Setup Started ==="

# 1. 仮想環境の作成
if [ ! -d ".venv" ]; then
    echo "[1/3] Creating virtual environment (.venv)..."
    python3 -m venv .venv
else
    echo "[1/3] Virtual environment already exists."
fi

# 2. 依存ライブラリのインストール
echo "[2/3] Installing dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3. カメラ権限の確認と付与
echo "[3/3] Checking camera permissions..."
if groups $USER | grep &>/dev/null '\bvideo\b'; then
    echo "User '$USER' is already in 'video' group."
else
    echo "Adding user '$USER' to 'video' group..."
    sudo usermod -aG video $USER
    echo "PLEASE REBOOT your Raspberry Pi for permissions to take effect!"
fi

echo "=== Setup Completed! ==="
echo "Please edit .env file before running."
