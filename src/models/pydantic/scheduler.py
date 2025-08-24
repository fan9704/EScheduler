from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, validator, ConfigDict
from tortoise.contrib.pydantic import pydantic_model_creator
from src.models.tortoise.scheduler import ScheduledTask, TaskExecution
from src.models.enum.scheduler import TaskState, TargetType, ExecutionStatus, ScheduleType


# Tortoise Pydantic 模型
ScheduledTaskPydantic = pydantic_model_creator(ScheduledTask)
TaskExecutionPydantic = pydantic_model_creator(TaskExecution)


class ScheduledTaskCreate(BaseModel):
    """創建排程任務請求模型"""
    name: str = Field(..., min_length=1, max_length=255, description="任務名稱")
    description: Optional[str] = Field(None, description="任務描述")
    schedule_expression: str = Field(..., description="排程表達式")
    schedule_type: Optional[ScheduleType] = Field(None, description="排程類型")
    execute_at: Optional[datetime] = Field(None, description="指定執行時間 (用於一次性任務)")
    timezone: str = Field("Asia/Taipei", description="時區")
    target_type: TargetType = Field(..., description="目標類型")
    target_arn: str = Field(..., description="目標 ARN 或 URL")
    target_input: Optional[Dict[str, Any]] = Field(None, description="目標輸入參數")
    max_retry_attempts: int = Field(3, ge=0, le=10, description="最大重試次數")
    retry_policy: Optional[Dict[str, Any]] = Field(None, description="重試策略")
    dead_letter_config: Optional[Dict[str, Any]] = Field(None, description="死信佇列配置")
    
    @validator('schedule_expression')
    def validate_schedule_expression(cls, v, values):
        """驗證排程表達式格式"""
        schedule_type = values.get('schedule_type')
        execute_at = values.get('execute_at')
        
        # 如果指定了執行時間，則為一次性任務
        if execute_at:
            return f"at({execute_at.isoformat()})"
        
        # 檢查表達式格式
        if v.startswith('cron(') and v.endswith(')'):
            return v
        elif v.startswith('rate(') and v.endswith(')'):
            return v
        elif v.startswith('at(') and v.endswith(')'):
            return v
        elif v.startswith('once'):
            return v
        else:
            raise ValueError('排程表達式必須是 cron(expression)、rate(expression)、at(datetime) 或 once 格式')
    
    @validator('execute_at')
    def validate_execute_at(cls, v):
        """驗證執行時間"""
        if v and v <= datetime.now():
            raise ValueError('執行時間必須是未來時間')
        return v


class ScheduledTaskUpdate(BaseModel):
    """更新排程任務請求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    schedule_expression: Optional[str] = None
    execute_at: Optional[datetime] = None
    timezone: Optional[str] = None
    target_type: Optional[TargetType] = None
    target_arn: Optional[str] = None
    target_input: Optional[Dict[str, Any]] = None
    state: Optional[TaskState] = None
    max_retry_attempts: Optional[int] = Field(None, ge=0, le=10)
    retry_policy: Optional[Dict[str, Any]] = None
    dead_letter_config: Optional[Dict[str, Any]] = None


class ScheduledTaskResponse(BaseModel):
    """排程任務回應模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: Optional[str]
    schedule_expression: str
    timezone: str
    target_type: str
    target_arn: str
    target_input: Optional[Dict[str, Any]]
    state: str
    last_execution_time: Optional[datetime]
    next_execution_time: Optional[datetime]
    execution_count: int
    max_retry_attempts: int
    retry_policy: Optional[Dict[str, Any]]
    dead_letter_config: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


# 新增：一次性任務創建模型
class OneTimeTaskCreate(BaseModel):
    """創建一次性任務請求模型"""
    name: str = Field(..., min_length=1, max_length=255, description="任務名稱")
    description: Optional[str] = Field(None, description="任務描述")
    execute_at: datetime = Field(..., description="執行時間")
    timezone: str = Field("Asia/Taipei", description="時區")
    target_type: TargetType = Field(..., description="目標類型")
    target_arn: str = Field(..., description="目標 ARN 或 URL")
    target_input: Optional[Dict[str, Any]] = Field(None, description="目標輸入參數")
    max_retry_attempts: int = Field(3, ge=0, le=10, description="最大重試次數")
    
    @validator('execute_at')
    def validate_execute_at(cls, v):
        """驗證執行時間必須是未來時間"""
        if v <= datetime.now():
            raise ValueError('執行時間必須是未來時間')
        return v


class TaskExecutionResponse(BaseModel):
    """任務執行記錄回應模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    task_id: int
    status: ExecutionStatus
    started_at: datetime
    completed_at: Optional[datetime]
    response_code: Optional[int]
    response_body: Optional[str]
    error_message: Optional[str]
    attempt_number: int


class SchedulerStatsResponse(BaseModel):
    """排程器統計回應模型"""
    total_tasks: int
    enabled_tasks: int
    disabled_tasks: int
    total_executions_today: int
    successful_executions_today: int
    failed_executions_today: int


class TaskStateUpdateRequest(BaseModel):
    """任務狀態更新請求模型"""
    state: TaskState = Field(..., description="新的任務狀態")