import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class SMTPConfig:
    """SMTP 配置"""

    host: str = "localhost"
    port: int = 587
    username: str = ""
    password: str = ""
    use_tls: bool = True
    use_ssl: bool = False
    default_from_email: str = "noreply@example.com"
    default_from_name: str = "EScheduler"

    @classmethod
    def from_env(cls) -> "SMTPConfig":
        """從環境變數載入配置"""
        return cls(
            host=os.getenv("SMTP_HOST", "localhost"),
            port=int(os.getenv("SMTP_PORT", "587")),
            username=os.getenv("SMTP_USERNAME", ""),
            password=os.getenv("SMTP_PASSWORD", ""),
            use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true",
            use_ssl=os.getenv("SMTP_USE_SSL", "false").lower() == "true",
            default_from_email=os.getenv("DEFAULT_FROM_EMAIL", "noreply@example.com"),
            default_from_name=os.getenv("DEFAULT_FROM_NAME", "EScheduler"),
        )


@dataclass
class HTTPConfig:
    """HTTP 配置"""

    timeout: int = 30
    max_retries: int = 3
    verify_ssl: bool = True

    @classmethod
    def from_env(cls) -> "HTTPConfig":
        """從環境變數載入配置"""
        return cls(
            timeout=int(os.getenv("HTTP_TIMEOUT", "30")),
            max_retries=int(os.getenv("HTTP_MAX_RETRIES", "3")),
            verify_ssl=os.getenv("HTTP_VERIFY_SSL", "true").lower() == "true",
        )


@dataclass
class WebhookConfig:
    """Webhook 配置"""

    timeout: int = 30
    max_retries: int = 3
    verify_ssl: bool = True

    @classmethod
    def from_env(cls) -> "WebhookConfig":
        """從環境變數載入配置"""
        return cls(
            timeout=int(os.getenv("WEBHOOK_TIMEOUT", "30")),
            max_retries=int(os.getenv("WEBHOOK_MAX_RETRIES", "3")),
            verify_ssl=os.getenv("WEBHOOK_VERIFY_SSL", "true").lower() == "true",
        )


@dataclass
class RabbitMQConfig:
    """RabbitMQ 配置"""

    host: str = "localhost"
    port: int = 5672
    username: str = "guest"
    password: str = "guest"
    virtual_host: str = "/"
    connection_url: Optional[str] = None

    @classmethod
    def from_env(cls) -> "RabbitMQConfig":
        """從環境變數載入配置"""
        # 如果有完整的連接 URL，直接使用
        connection_url = os.getenv("RABBITMQ_CONNECTION_URL")
        if connection_url:
            return cls(connection_url=connection_url)

        # 否則從個別環境變數組合
        host = os.getenv("RABBITMQ_HOST", "localhost")
        port = int(os.getenv("RABBITMQ_PORT", "5672"))
        username = os.getenv("RABBITMQ_USERNAME", "guest")
        password = os.getenv("RABBITMQ_PASSWORD", "guest")
        virtual_host = os.getenv("RABBITMQ_VIRTUAL_HOST", "/")

        connection_url = f"amqp://{username}:{password}@{host}:{port}{virtual_host}"

        return cls(
            host=host,
            port=port,
            username=username,
            password=password,
            virtual_host=virtual_host,
            connection_url=connection_url,
        )


class StrategyConfigManager:
    """策略配置管理器"""

    def __init__(self):
        self._smtp_config: Optional[SMTPConfig] = None
        self._http_config: Optional[HTTPConfig] = None
        self._webhook_config: Optional[WebhookConfig] = None
        self._rabbitmq_config: Optional[RabbitMQConfig] = None

    @property
    def smtp(self) -> SMTPConfig:
        """獲取 SMTP 配置"""
        if self._smtp_config is None:
            self._smtp_config = SMTPConfig.from_env()
        return self._smtp_config

    @property
    def http(self) -> HTTPConfig:
        """獲取 HTTP 配置"""
        if self._http_config is None:
            self._http_config = HTTPConfig.from_env()
        return self._http_config

    @property
    def webhook(self) -> WebhookConfig:
        """獲取 Webhook 配置"""
        if self._webhook_config is None:
            self._webhook_config = WebhookConfig.from_env()
        return self._webhook_config

    @property
    def rabbitmq(self) -> RabbitMQConfig:
        """獲取 RabbitMQ 配置"""
        if self._rabbitmq_config is None:
            self._rabbitmq_config = RabbitMQConfig.from_env()
        return self._rabbitmq_config

    def reload_config(self):
        """重新載入所有配置"""
        self._smtp_config = None
        self._http_config = None
        self._webhook_config = None
        self._rabbitmq_config = None


# 全域配置管理器實例
config_manager = StrategyConfigManager()


# 便捷函數
def get_smtp_config() -> SMTPConfig:
    """獲取 SMTP 配置"""
    return config_manager.smtp


def get_http_config() -> HTTPConfig:
    """獲取 HTTP 配置"""
    return config_manager.http


def get_webhook_config() -> WebhookConfig:
    """獲取 Webhook 配置"""
    return config_manager.webhook


def get_rabbitmq_config() -> RabbitMQConfig:
    """獲取 RabbitMQ 配置"""
    return config_manager.rabbitmq
