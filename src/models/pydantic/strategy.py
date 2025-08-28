
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from src.configs.cfg import TZ

class ExecutionResult(BaseModel):
    """執行結果封裝類"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="訊息內容")
    data: Dict[str, Any] = Field(default_factory=dict, description="附加資料")
    execution_time: float = Field(default=0.0, description="執行時間（秒）")
    status_code: Optional[int] = Field(default=None, description="狀態碼")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo(TZ)), description="時間戳")