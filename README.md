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
- カメラデバイス:
    - **USB Webカメラ**: そのままUSBポートに接続
    - **HDMI入力機器**: ラズパイ本体のHDMIは「出力専用」です。**HDMI-USBキャプチャボード（千円程度〜）** が別途必要になります。
- Slack App (Bot Token と App Token)
- OpenCV (`pip install opencv-python-headless`)

## インストール

1. リポジトリをダウンロードします。

   ```bash
   # 初回のみ（ダウンロード）
   # ※ URLは自分のリポジトリのものを使ってください
   # ※ 末尾のフォルダ名指定を省略すると、リポジトリ名と同じフォルダが作られます
   # ※ 自由にフォルダ名を指定しても構いません (例: my_bot)
   git clone https://github.com/yktsuruoka/asahibot.git my_bot
   
   # 作成されたフォルダに移動（リポジトリ名によって変わります）
   cd my_bot
   
   # 2回目以降（更新）
   git pull
   ```

2. インストールスクリプトを実行します。
   これだけで「仮想環境の作成」から「ライブラリのインストール」「権限設定」まで自動で行われます。

   ```bash
   ./setup.sh
   ```

   ※ 権限設定が変更された場合（初回など）、再起動を促すメッセージが表示されます。その場合は `sudo reboot` してください。

## Slack Tokenの取得方法

1.  **Slack Appの作成**: [Slack API](https://api.slack.com/apps) にアクセスし、「Create New App」→「From scratch」を選択。
2.  **App Token (SLACK_APP_TOKEN)**:
    *   左メニュー「Basic Information」→「App-Level Tokens」までスクロール。
    *   「Generate Token and Scopes」をクリック。
    *   Scopeに `connections:write` を追加し、名前を適当に付けてGenerate。
    *   `xapp-` から始まるトークンをコピーします。
3.  **Bot Token (SLACK_BOT_TOKEN)**:
    *   左メニュー「OAuth & Permissions」を選択。
    *   「Scopes」→「Bot Token Scopes」に以下を追加:
        *   `chat:write`: 画像をアップロードするため
        *   `files:write`: 画像を保存・送信するため
    *   ページ上部の「Install to Workspace」をクリックして許可。
        > **注意**: ワークスペースの設定によっては、**管理者の承認** が必要な場合があります。その場合は管理者にリクエストを送ってください。
    *   `xoxb-` から始まる「Bot User OAuth Token」をコピーします。
4.  **イベントの購読 (Event Subscriptions)**:
    *   左メニュー **「Event Subscriptions」** を選択し、スイッチを **ON** にします。
    *   **「Subscribe to bot events」** を展開し、以下を追加します:
        *   `message.im`: DMを受け取るため
    *   **「Save Changes」** をクリックします（画面下部）。
    *   ※ページ上部に「Reinstall your app」と出たらクリックして再インストールしてください。
5.  **Socket Modeの有効化**:
    *   左メニュー「Socket Mode」→「Enable Socket Mode」をONにします。
6.  **DMの許可 (App Home)**:
    *   左メニュー「App Home」を選択。
    *   「Show Tabs」にある **「Messages Tab」** をONにします。
    *   `Allow users to send Slash commands and messages from the messages tab` にチェックが入っていることを確認します。

## 設定

1. `.env.example` をコピーして `.env` ファイルを作成します。

   > **注意**: `.env` や `.env.example` は、ファイル名の先頭にドットが付いているため **「隠しファイル」** として扱われます。
   > フォルダ画面で見えない場合は、**`Ctrl + H`** を押すか、設定で「隠しファイルを表示」を有効にしてください。

   ```bash
   cp .env.example .env
   ```
2. `.env` ファイルをエディタで開き、設定を書き換えます。

   **コマンド画面(CUI)の場合**:
   ```bash
   nano .env
   ```
   *   編集が終わったら `Ctrl+O` で保存、`Enter` で確定、`Ctrl+X` で終了します。

   **デスクトップ画面(GUI)の場合**:
   *   `.env` ファイルを右クリックして「テキストエディタで開く (Text Editor)」を選択してください。
   *   内容を書き換えて、普通に「保存」してください。
   ```ini
   SLACK_BOT_TOKEN=xoxb-...
   SLACK_APP_TOKEN=xapp-...
   SAVE_DIRECTORY=data
   CAMERA_DEVICE=/dev/video0
   CAMERA_RESOLUTION=1920x1080
   ```

## 起動方法

以下のスクリプトを実行するだけで、仮想環境の有効化と実行をまとめて行います。

```bash
# 初回のみ実行権限を付与
chmod +x start.sh

# 実行
./start.sh
```

### 自動起動する場合 (systemd)

以下のコマンドを1回実行するだけで、自動起動の設定が完了します。

```bash
./start.sh --install
```

これで、Raspberry Piの起動時にボットが自動的に立ち上がるようになります。

## 使い方

ボットの起動中、以下の操作を行うと、カメラで写真を撮影して返信します。

*   **DM (ダイレクトメッセージ) を送る**: ボットに対して直接メッセージを送る（内容は「撮影して」など何でもOK）。

数秒後に撮影された画像が返信されます。

## 画像の保存と管理

*   撮影された画像は `data/` ディレクトリ（または環境変数で指定した場所）に保存されます。
*   容量圧迫を防ぐため、**撮影時に「7日以上経過した古い画像」は自動的に削除**されます。

## ファイル構成

*   `setup.sh`: **インストール用スクリプト**（環境構築 & 権限設定）
*   `start.sh`: **起動・設定用スクリプト**（手動起動 & 自動起動設定）

*   `app.py`: ボットのメインプログラム
*   `asahibot.service`: 自動起動用の設定ファイル
*   `requirements.txt`: 必要なPythonライブラリ一覧
*   `.env.example`: 設定ファイルのテンプレート

## 注意事項
*   `.env` ファイルには秘密情報（トークン）が含まれるため、他人に共有しないよう注意してください。
