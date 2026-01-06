#!/bin/bash

# スクリプトのあるディレクトリに移動
cd "$(dirname "$0")"

# --- Install Mode ---
if [ "$1" == "--install" ]; then
    echo "Installing asahibot service..."
    
    # サービスファイルのコピー
    echo "Copying service file to /etc/systemd/system/..."
    sudo cp asahibot.service /etc/systemd/system/
    
    # 反映と有効化
    echo "Reloading daemon and enabling service..."
    sudo systemctl daemon-reload
    sudo systemctl enable asahibot
    sudo systemctl start asahibot
    
    echo "Done! AsahiBot is now running as a service."
    exit 0
fi

# --- Normal Execution Mode ---
# 仮想環境を有効化して実行
source .venv/bin/activate
python3 app.py
