import os
import warnings
import logging
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

logger = logging.getLogger(__name__)

# 特定の警告を無視
warnings.filterwarnings("ignore", category=RuntimeWarning, module="pyftpdlib.authorizers")

class CustomFTPHandler(FTPHandler):
    def on_file_received(self, file):
        logger.info(f"File received: {file}")

def run_ftp_server(directory, port=2121):
    authorizer = DummyAuthorizer()
    authorizer.add_anonymous(directory, perm="elradfmwMT")

    handler = CustomFTPHandler
    handler.authorizer = authorizer

    server = FTPServer(("0.0.0.0", port), handler)
    logger.info(f"FTP server is running on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    upload_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    run_ftp_server(upload_dir)
    