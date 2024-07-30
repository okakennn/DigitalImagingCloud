import os
import hashlib
import sqlite3
import logging
import threading
from cloud_uploader import upload_to_google_photos
from utils.config_loader import CONFIG

logger = logging.getLogger(__name__)

class UploadManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.file_locks = {}
        self.create_table()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def create_table(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS uploads
            (file_hash TEXT PRIMARY KEY, file_name TEXT, upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
            ''')

    def calculate_file_hash(self, file_path):
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as file:
            buf = file.read(CONFIG['upload']['hash_buffer_size'])
            while len(buf) > 0:
                hasher.update(buf)
                buf = file.read(CONFIG['upload']['hash_buffer_size'])
        return hasher.hexdigest()

    def is_file_uploaded(self, file_hash):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM uploads WHERE file_hash = ?', (file_hash,))
            return cursor.fetchone() is not None

    def record_upload(self, file_hash, file_name):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT OR REPLACE INTO uploads (file_hash, file_name) VALUES (?, ?)',
                           (file_hash, file_name))

    def handle_file(self, file_path):
        file_name = os.path.basename(file_path)
        file_lock = self.file_locks.setdefault(file_name, threading.Lock())

        with file_lock:
            with self.lock:
                file_hash = self.calculate_file_hash(file_path)

                if self.is_file_uploaded(file_hash):
                    logger.info(f"File {file_name} has already been uploaded. Skipping.")
                    try:
                        os.remove(file_path)
                        logger.info(f"Deleted duplicate file: {file_name}")
                    except OSError as e:
                        logger.error(f"Error deleting duplicate file {file_name}: {e}")
                    return

                try:
                    upload_result = upload_to_google_photos(file_path)
                    if upload_result:
                        self.record_upload(file_hash, file_name)
                        logger.info(f"Successfully uploaded and recorded: {file_name}")
                        if CONFIG['upload']['delete_after_upload']:
                            os.remove(file_path)
                            logger.info(f"Deleted uploaded file: {file_name}")
                    else:
                        logger.error(f"Failed to upload {file_name}")
                except Exception as e:
                    logger.error(f"Error processing {file_name}: {str(e)}")

        del self.file_locks[file_name]

if __name__ == "__main__":
    upload_manager = UploadManager(CONFIG['upload']['history_db'])
    test_file_path = "path/to/your/test/image.jpg"
    upload_manager.handle_file(test_file_path)
