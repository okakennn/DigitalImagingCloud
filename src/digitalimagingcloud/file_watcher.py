import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from utils.config_loader import CONFIG

logger = logging.getLogger(__name__)

class ImageHandler(FileSystemEventHandler):
    def __init__(self, upload_function, stability_timeout, check_interval):
        self.upload_function = upload_function
        self.stability_timeout = stability_timeout
        self.check_interval = check_interval

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(tuple(CONFIG['file_watcher']['allowed_extensions'])):
            logger.info(f"New file detected: {event.src_path}")
            if self.wait_for_file_stability(event.src_path):
                self.upload_function(event.src_path)
            else:
                logger.warning(f"File {event.src_path} is unstable or not found. Skipping.")

    def wait_for_file_stability(self, file_path):
        start_time = time.time()
        last_size = -1
        while time.time() - start_time < self.stability_timeout:
            try:
                current_size = os.path.getsize(file_path)
                if current_size == last_size:
                    return True
                last_size = current_size
            except FileNotFoundError:
                return False
            time.sleep(self.check_interval)
        return False

def watch_directory(directory, upload_function, stability_timeout, check_interval):
    event_handler = ImageHandler(upload_function, stability_timeout, check_interval)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=True)
    observer.start()
    logger.info(f"Started watching directory: {directory}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("File watcher stopped")
    observer.join()

if __name__ == "__main__":
    def dummy_upload(file_path):
        print(f"Uploading {file_path}")

    watch_directory(
        CONFIG['ftp']['upload_dir'],
        dummy_upload,
        CONFIG['file_watcher']['stability_timeout'],
        CONFIG['file_watcher']['check_interval']
    )
