import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

class ImageHandler(FileSystemEventHandler):
    def __init__(self, upload_function):
        self.upload_function = upload_function

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(('.jpg', '.jpeg')):
            logger.info(f"New JPEG file detected: {event.src_path}")
            self.upload_function(event.src_path)

def watch_directory(directory, upload_function):
    event_handler = ImageHandler(upload_function)
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
    