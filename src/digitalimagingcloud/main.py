import os
import threading
from ftp_server import run_ftp_server
from file_watcher import watch_directory
from cloud_uploader import upload_to_google_photos
from utils.logging_config import setup_logging

def handle_uploaded_file(file_path):
    logger.info(f"New file uploaded: {file_path}")
    upload_to_google_photos(file_path)

def main():
    global logger
    logger = setup_logging()

    upload_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    logger.info(f"Upload directory created: {upload_dir}")

    # FTPサーバーを別スレッドで起動
    ftp_thread = threading.Thread(target=run_ftp_server, args=(upload_dir,))
    ftp_thread.start()
    logger.info("FTP server thread started")

    # ファイル監視とアップロードを開始
    logger.info("Starting file watcher")
    watch_directory(upload_dir, handle_uploaded_file)

if __name__ == "__main__":
    main()
    