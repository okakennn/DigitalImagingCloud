import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(log_file='digital_imaging_cloud.log', log_level=logging.INFO):
    # ログディレクトリの作成（存在しない場合）
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # ルートロガーの設定
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # 既存のハンドラをすべて削除
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # フォーマッターの作成
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # ファイルハンドラの設定（ローテーション付き）
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
