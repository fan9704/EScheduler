import logging
import os
import sys
import datetime as dt
from logging.handlers import RotatingFileHandler
from multiprocessing import Queue
from logging_loki import LokiQueueHandler
from pythonjsonlogger import json
from src.configs import TZ

# 基本日誌配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
JSON_LOG_FORMAT = '%(timestamp)s %(level)s %(name)s %(message)s'

# 日誌文件配置
LOG_DIR = 'logs'
MAX_BYTES = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5

# Loki 配置
ENABLE_LOKI_LOGGING = bool(os.getenv('ENABLE_LOKI_LOGGING', False) == "True")
LOKI_ENDPOINT = os.getenv(
    'LOKI_ENDPOINT', 'http://127.0.0.1:3100/loki/api/v1/push')


def setup_logger(name='fastapi-app'):
    """設定結構化日誌系統

    Args:
        name (str): 日誌記錄器名稱

    Returns:
        logging.Logger: 配置好的日誌記錄器實例
    """
    logger_instance = logging.getLogger(name)
    logger_instance.setLevel(getattr(logging, LOG_LEVEL.upper()))

    # 確保日誌目錄存在
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # 配置控制台輸出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger_instance.addHandler(console_handler)

    # 配置文件輸出（JSON格式）
    json_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, f'{name}.json'),
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT
    )
    json_formatter = json.JsonFormatter(JSON_LOG_FORMAT)
    json_handler.setFormatter(json_formatter)
    logger_instance.addHandler(json_handler)

    # 配置錯誤日誌
    error_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, f'{name}.error.log'),
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger_instance.addHandler(error_handler)
    if ENABLE_LOKI_LOGGING:
        # 配置 Loki 輸出
        loki_handler = LokiQueueHandler(
            Queue(-1),
            url=LOKI_ENDPOINT,
            tags={'application': name},
            version='1'
        )
        logger_instance.addHandler(loki_handler)

    return logger_instance


# Init log instance
logger = setup_logger()


# def log_exception(logger_instance, exc_info=None):
#     """記錄異常詳細信息
#
#     Args:
#         logger (logging.Logger): 日誌記錄器實例
#         exc_info: 異常信息，默認為當前異常
#     """
#     logger_instance.error(
#         'Exception occurred',
#         exc_info=exc_info or sys.exc_info(),
#         extra={
#             'timestamp': dt.datetime.now(TZ).isoformat(),
#             'error_type': str(sys.exc_info()[0].__name__),
#             'error_message': str(sys.exc_info()[1])
#         }
#     )
