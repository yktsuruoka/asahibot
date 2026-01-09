#!/bin/bash

# スクリプトのあるディレクトリに移動
cd "$(dirname "$0")"

# --- Install Mode ---
if [ "$1" == "--install" ]; then
    echo "Installing asahibot service..."
    
    # ユーザーとパスの取得
    CURRENT_USER=$(whoami)
    CURRENT_DIR=$(pwd)
    SERVICE_NAME="asahibot.service"
    
    echo "Configuring service for User: $CURRENT_USER, Path: $CURRENT_DIR"

    # サービスファイルの生成（テンプレートの置換）
    sed -e "s|%USER%|$CURRENT_USER|g" \
        -e "s|%WORKDIR%|$CURRENT_DIR|g" \
        asahibot.service > /tmp/$SERVICE_NAME

    echo "Copying service file to /etc/systemd/system/..."
    sudo cp /tmp/$SERVICE_NAME /etc/systemd/system/
    rm /tmp/$SERVICE_NAME
    
    # 反映と有効化
    echo "Reloading daemon and enabling service..."
    sudo systemctl daemon-reload
    sudo systemctl enable asahibot
    sudo systemctl start asahibot
    
    echo "Done! Service 'asahibot' is now running."
    exit 0
fi

# --- Normal Execution Mode ---
# 仮想環境を有効化して実行
source .venv/bin/activate
python3 app.py
