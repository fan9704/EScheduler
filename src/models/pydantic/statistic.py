from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class StatisticDashboardMetricResponse(BaseModel):
    """統計儀表板指標回應模型"""
    model_config = ConfigDict(from_attributes=True)  # Pydantic v2 配置
    
    total_tasks: Optional[int] = Field(default=0, description="總任務數")
    enabled_tasks: Optional[int] = Field(default=0, description="啟用的任務數")
    disabled_tasks: Optional[int] = Field(default=0, description="禁用的任務數")
    today_executions_count: Optional[int] = Field(default=0, description="今天的任務執行次數")