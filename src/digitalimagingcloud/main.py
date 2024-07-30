import os
import threading
from ftp_server import run_ftp_server
from file_watcher import watch_directory
from upload_manager import UploadManager
from utils.logging_config import setup_logging
from utils.config_loader import CONFIG

upload_manager = None

def handle_uploaded_file(file_path):
    global upload_manager
    logger.info(f"New file uploaded: {file_path}")
    upload_manager.handle_file(file_path)

def main():
    global logger, upload_manager
    logger = setup_logging(
        log_file=CONFIG['logging']['file'],
        log_level=CONFIG['logging']['level']
    )

    upload_dir = os.path.join(os.getcwd(), CONFIG['ftp']['upload_dir'])
    os.makedirs(upload_dir, exist_ok=True)
    logger.info(f"Upload directory created: {upload_dir}")

    upload_manager = UploadManager(CONFIG['upload']['history_db'])

    # FTPサーバーを別スレッドで起動
    ftp_thread = threading.Thread(
        target=run_ftp_server,
        args=(upload_dir, CONFIG['ftp']['port'], CONFIG['ftp']['anonymous_login'])
    )
    ftp_thread.start()
    logger.info("FTP server thread started")

    # ファイル監視とアップロードを開始
    logger.info("Starting file watcher")
    watch_directory(
        upload_dir,
        handle_uploaded_file,
        CONFIG['file_watcher']['stability_timeout'],
        CONFIG['file_watcher']['check_interval']
    )

if __name__ == "__main__":
    main()
