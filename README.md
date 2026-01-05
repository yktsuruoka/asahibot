# Slack Camera Bot

Slack からのメンションなどのイベントを受け取り、接続されたカメラで写真を撮影して返信するボットです。

## 特徴
- Slack Socket Mode を使用（ファイアウォール設定不要）
- 撮影画像をローカルに保存し、Slack にアップロード
- **OpenCV** による柔軟なカメラ制御（HDMIキャプチャ対応）
- **自動お掃除機能**: 7日以上経過した古い画像は自動的に削除
- 環境変数による設定管理

## 必要要件
- **Raspberry Pi (推奨)** または Linux PC
- Python 3.x
- カメラ（USB Webカメラ, HDMI-USB変換アダプタ等）
- Slack App (Bot Token と App Token)
- OpenCV (`pip install opencv-python-headless`)

## インストール

1. リポジトリをダウンロード（または配置）します。
2. 仮想環境を作成し、依存ライブラリをインストールします。
   ```bash
   # 仮想環境の作成
   python3 -m venv .venv
   
   # アクティベート
   source .venv/bin/activate
   
   # ライブラリインストール
   pip install -r requirements.txt
   ```
3. カメラデバイスへのアクセス権限を設定します（初回のみ）。
   ```bash
   sudo usermod -aG video $USER
   sudo reboot
   ```

## 設定

1. `.env.example` をコピーして `.env` ファイルを作成します。
   ```bash
   cp .env.example .env
   ```
2. `.env` ファイルを編集し、以下の項目を設定します。
   ```ini
   SLACK_BOT_TOKEN=xoxb-...
   SLACK_APP_TOKEN=xapp-...
   SAVE_DIRECTORY=data
   CAMERA_DEVICE=/dev/video0
   CAMERA_RESOLUTION=1920x1080
   ```

## 起動方法

仮想環境のPythonを使用して実行します。

```bash
# 仮想環境を有効化していない場合
.venv/bin/python3 app.py
```

または

```bash
# 仮想環境を有効化してから実行
source .venv/bin/activate
python3 app.py
```

## 画像の保存と管理

*   撮影された画像は `data/` ディレクトリ（または環境変数で指定した場所）に保存されます。
*   容量圧迫を防ぐため、**撮影時に「7日以上経過した古い画像」は自動的に削除**されます。

## ファイル構成

*   `app.py`: ボットのメインプログラム
*   `requirements.txt`: 必要なPythonライブラリ一覧
*   `.env.example`: 設定ファイルのテンプレート

## 注意事項
*   `.env` ファイルには秘密情報（トークン）が含まれるため、他人に共有しないよう注意してください。
