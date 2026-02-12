import datetime as dt
from zoneinfo import ZoneInfo
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from src.configs.cfg import TZ


class StrategyBaseResult(BaseModel):
    """所有 Result 的基底"""

    pass


class RabbitMQResult(StrategyBaseResult):
    """RabbitQM 結果封裝"""

    target: str = Field(..., description="目標 Queue 或 Exchange 資訊")
    message_body: Dict[str, Any] = Field(..., description="訊息內容")
    properties: Dict[str, Any] = Field(
        default_factory=dict, description="訊息屬性 (如 TTL, Priority)"
    )
    queue_args: Dict[str, Any] = Field(
        default_factory=dict, description="Queue 參數 (如死信, 最大優先級)"
    )
    message_size: int = Field(..., description="訊息大小 (bytes)")


class HTTPResult(StrategyBaseResult):
    """HTTP 結果封裝"""

    method: str = Field(..., description="HTTP 方法 (GET, POST, ...)")
    url: str = Field(..., description="請求的 URL")
    request_headers: Dict[str, Any] = Field(
        default_factory=dict, description="請求標頭"
    )
    request_params: Dict[str, Any] = Field(default_factory=dict, description="查詢參數")
    request_data: Optional[Any] = Field(
        None, description="請求資料 (POST body, JSON, ...)"
    )
    response_body: Optional[str] = Field(None, description="回應內容 (純文字/JSON字串)")
    response_headers: Dict[str, Any] = Field(
        default_factory=dict, description="回應標頭"
    )


class WebhookResult(StrategyBaseResult):
    """Webhook 結果封裝"""

    method: str = Field(..., description="HTTP 方法 (POST, GET, ...)")
    url: str = Field(..., description="Webhook 目標 URL")
    body: Optional[Any] = Field(None, description="請求的主體內容 (JSON 或字串)")
    has_signature: bool = Field(False, description="是否包含簽名驗證 (取決於 secret)")
    response_body: Optional[str] = Field(None, description="Webhook 回應內容")
    response_headers: Dict[str, Any] = Field(
        default_factory=dict, description="Webhook 回應標頭"
    )


class ExecutionResult(BaseModel):
    """執行結果封裝類"""

    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="訊息內容")
    data: Optional[StrategyBaseResult] = Field(default=None, description="附加資料")
    execution_time: float = Field(default=0.0, description="執行時間（秒）")
    status_code: Optional[int] = Field(default=None, description="狀態碼")
    timestamp: dt.datetime = Field(
        default_factory=lambda: dt.datetime.now(ZoneInfo(TZ)), description="時間戳"
    )
