import os
import datetime
import time
import subprocess
from slack_sdk import WebClient
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

import cv2


# 環境変数を読み込む
load_dotenv()

# 設定
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
SAVE_DIRECTORY = os.environ.get("SAVE_DIRECTORY", "data")
CAMERA_DEVICE = os.environ.get("CAMERA_DEVICE", "/dev/video0")
CAMERA_RESOLUTION = os.environ.get("CAMERA_RESOLUTION", "1920x1080")

# ... (omitted directory check code) ...

def capture_image(filepath, say=None):
    """
    OpenCVを使って画像をキャプチャする関数。失敗時はFalseを返し、呼び出し元でエラー通知を行う。
    """
    capture_success = False
    last_error = None
    
    # Check device ID
    device_id = 0
    if CAMERA_DEVICE.startswith("/dev/video"):
        try:
            device_id = int(CAMERA_DEVICE.replace("/dev/video", ""))
        except:
            device_id = 0
    elif CAMERA_DEVICE.isdigit():
        device_id = int(CAMERA_DEVICE)
        
    print(f"Attempting capture with OpenCV (Device {device_id})...")
    
    try:
        cap = cv2.VideoCapture(device_id)
        if not cap.isOpened():
            raise Exception(f"Could not open video device {device_id}")

        # Set resolution and format
        # 1920x1080
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        # Try to force MJPG
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
        
        # Buffer clear / Warmup (1.5 seconds)
        # カメラの露出調整やバッファクリアのために空読みする
        start_time = time.time()
        while time.time() - start_time < 1.5:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
        
        # Actual capture
        ret, frame = cap.read()
        
        if ret and frame is not None:
            cv2.imwrite(filepath, frame)
            # Check file
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                print(f"Saved image to {filepath}")
                capture_success = True
            else:
                last_error = "File save failed or empty."
        else:
            last_error = "Failed to grab frame (ret=False)"
            
        cap.release()
        
    except Exception as e:
        last_error = str(e)
        print(f"OpenCV capture failed: {last_error}")

    if capture_success:
        return True
    else:
        print(f"Capture failed. Last error: {last_error}")
        if say:
            say(f"Error: Capture failed (p: {device_id}).\nDetails: {last_error}")
        return False

# ディレクトリが存在しない場合は作成
if not os.path.exists(SAVE_DIRECTORY):
    os.makedirs(SAVE_DIRECTORY)

# アプリを初期化
if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN:
    print("Error: SLACK_BOT_TOKEN and SLACK_APP_TOKEN must be set in .env file.")
    exit(1)

app = App(token=SLACK_BOT_TOKEN)
client = WebClient(token=SLACK_BOT_TOKEN)

@app.message("")
def message_hello(message, say):
    user = message['user']
    channel_id = message['channel']

    print(f"Received message from {user} in {channel_id}")

    # 画像保存パス
    filename = f"capture_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = os.path.join(SAVE_DIRECTORY, filename)

    # 古いファイルの削除 (7日以上前)
    cleanup_old_files(SAVE_DIRECTORY, days=7)

    capture_success = capture_image(filepath, say)

    if capture_success:
        # ログ保存
        now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        log_path = os.path.join(SAVE_DIRECTORY, "output.log")
        output = "%s %s\n" % (now, user)
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(output)
        except Exception as e:
            print(f"Log write failed: {e}")

        # Slackにアップロード
        try:
            client.files_upload_v2(
                file=filepath,
                channel=channel_id,
                initial_comment=f"Captured at {now}"
            )
        except Exception as e:
            print(f"Error uploading file: {e}")
            say(f"Error uploading file: {e}")



def cleanup_old_files(directory, days=7):
    """
    指定日数より古いファイルを削除する関数
    """
    cutoff = time.time() - (days * 86400)
    print(f"Running cleanup for files older than {days} days in {directory}...")
    try:
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                # タイムスタンプ取得 (最終更新日時)
                mtime = os.path.getmtime(filepath)
                if mtime < cutoff:
                    try:
                        os.remove(filepath)
                        print(f"Deleted old file: {filename}")
                    except Exception as e:
                        print(f"Failed to delete {filename}: {e}")
    except Exception as e:
        print(f"Cleanup failed: {e}")

if __name__ == "__main__":
    print("Starting Slack Bot (OpenCV version)...")
    SocketModeHandler(app, SLACK_APP_TOKEN).start()