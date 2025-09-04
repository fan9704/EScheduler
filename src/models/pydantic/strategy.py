
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from src.configs.cfg import TZ

class RabbitMQResult(BaseModel):
    """RabbitQM結果封裝"""
    target: str = Field(..., description="目標 Queue 或 Exchange 資訊")
    message_body: Dict[str, Any] = Field(..., description="訊息內容")
    properties: Dict[str, Any] = Field(default_factory=dict, description="訊息屬性 (如 TTL, Priority)")
    queue_args: Dict[str, Any] = Field(default_factory=dict, description="Queue 參數 (如死信, 最大優先級)")
    message_size: int = Field(..., description="訊息大小 (bytes)")

class ExecutionResult(BaseModel):
    """執行結果封裝類"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="訊息內容")
    data: RabbitMQResult = Field(default_factory=RabbitMQResult, description="附加資料")
    execution_time: float = Field(default=0.0, description="執行時間（秒）")
    status_code: Optional[int] = Field(default=None, description="狀態碼")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo(TZ)), description="時間戳")