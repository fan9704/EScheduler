import os
from typing import Optional

# SMTP 配置
SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
SMTP_USE_SSL = os.getenv("SMTP_USE_SSL", "false").lower() == "true"

# 預設寄件人
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@example.com")
DEFAULT_FROM_NAME = os.getenv("DEFAULT_FROM_NAME", "EScheduler")


class SMTPSettings:
    """SMTP 設定類別"""
    
    def __init__(self):
        self.host = SMTP_HOST
        self.port = SMTP_PORT
        self.username = SMTP_USERNAME
        self.password = SMTP_PASSWORD
        self.use_tls = SMTP_USE_TLS
        self.use_ssl = SMTP_USE_SSL
        self.default_from_email = DEFAULT_FROM_EMAIL
        self.default_from_name = DEFAULT_FROM_NAME
    
    @property
    def is_configured(self) -> bool:
        """檢查 SMTP 是否已正確配置"""
        return bool(self.host and self.username and self.password)
    
    def get_connection_string(self) -> str:
        """獲取 SMTP 連接字串"""
        protocol = "smtps" if self.use_ssl else "smtp"
        return f"{protocol}://{self.username}:{self.password}@{self.host}:{self.port}"


def get_smtp_settings() -> SMTPSettings:
    """獲取 SMTP 設定實例"""
    return SMTPSettings()