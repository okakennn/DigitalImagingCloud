import os
import warnings
import logging
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from utils.config_loader import CONFIG

logger = logging.getLogger(__name__)

# 特定の警告を無視
warnings.filterwarnings("ignore", category=RuntimeWarning, module="pyftpdlib.authorizers")

class CustomFTPHandler(FTPHandler):
    def on_file_received(self, file):
        logger.info(f"File received: {file}")

def run_ftp_server(directory, port, allow_anonymous):
    authorizer = DummyAuthorizer()
    if allow_anonymous:
        authorizer.add_anonymous(directory, perm="elradfmwMT")
    else:
        # ここで必要に応じて認証ユーザーを追加
        username = CONFIG['ftp'].get('username', 'user')
        password = CONFIG['ftp'].get('password', 'password')
        authorizer.add_user(username, password, directory, perm="elradfmwMT")

    handler = CustomFTPHandler
    handler.authorizer = authorizer

    server = FTPServer(("0.0.0.0", port), handler)
    logger.info(f"FTP server is running on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    upload_dir = CONFIG['ftp']['upload_dir']
    port = CONFIG['ftp']['port']
    allow_anonymous = CONFIG['ftp']['anonymous_login']
    os.makedirs(upload_dir, exist_ok=True)
    run_ftp_server(upload_dir, port, allow_anonymous)