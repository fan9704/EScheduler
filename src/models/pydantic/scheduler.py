import datetime as dt
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, ConfigDict, field_validator
from tortoise.contrib.pydantic import pydantic_model_creator

from src.models.enum.scheduler import TaskState, TargetType, ExecutionStatus
from src.models.tortoise.scheduler import ScheduledTask, TaskExecution

# Tortoise Pydantic 模型
ScheduledTaskPydantic = pydantic_model_creator(ScheduledTask)
TaskExecutionPydantic = pydantic_model_creator(TaskExecution)


class ScheduledTaskCreate(BaseModel):
    """創建排程任務請求模型"""
    name: str = Field(..., min_length=1, max_length=255, description="任務名稱")
    description: Optional[str] = Field(None, description="任務描述")
    schedule_expression: str = Field(..., description="排程表達式")
    timezone: str = Field("Asia/Taipei", description="時區")
    target_type: TargetType = Field(..., description="目標類型")
    target_arn: str = Field(..., description="目標 ARN 或 URL")
    target_input: Optional[Dict[str, Any]] = Field(None, description="目標輸入參數")
    max_retry_attempts: int = Field(3, ge=0, le=10, description="最大重試次數")
    retry_policy: Optional[Dict[str, Any]] = Field(None, description="重試策略")
    dead_letter_config: Optional[Dict[str, Any]] = Field(None, description="死信佇列配置")
    state: TaskState = Field(default=TaskState.ENABLED, description="任務狀態")

    @field_validator('schedule_expression')
    @classmethod
    def validate_schedule_expression(cls, v):
        """驗證排程表達式格式"""
        if v.startswith('cron(') and v.endswith(')'):
            return v
        elif v.startswith('rate(') and v.endswith(')'):
            return v
        else:
            raise ValueError('排程表達式必須是 cron(expression) 或 rate(expression) 格式')


class ScheduledTaskUpdate(BaseModel):
    """更新排程任務請求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    schedule_expression: Optional[str] = None
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
    model_config = ConfigDict(from_attributes=True)  # Pydantic v2 配置

    id: int
    name: str
    description: Optional[str]
    schedule_expression: str
    timezone: str
    target_type: str
    target_arn: str
    target_input: Optional[Dict[str, Any]]
    state: str
    last_execution_time: Optional[dt.datetime]
    next_execution_time: Optional[dt.datetime]
    execution_count: int
    max_retry_attempts: int
    retry_policy: Optional[Dict[str, Any]]
    dead_letter_config: Optional[Dict[str, Any]]
    created_at: dt.datetime
    updated_at: dt.datetime


class TaskExecutionResponse(BaseModel):
    """任務執行記錄回應模型"""
    model_config = ConfigDict(from_attributes=True)  # Pydantic v2 配置

    id: int
    task_id: int
    status: ExecutionStatus
    started_at: dt.datetime
    completed_at: Optional[dt.datetime]
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


class SchedulerJob(BaseModel):
    id: int
    name: Optional[str]
    target_type: Optional[str]
    target_arn: Optional[str]
    target_input: Optional[Dict[str, Any]] = Field(default={})


class InternalSchedulerJob(BaseModel):
    id: int
    name: str
    next_run_time: Optional[dt.datetime]
    trigger: str


class InternalJobStatusResponse(BaseModel):
    exists: bool
    next_run_time: Optional[str] = None
    trigger: Optional[str] = None
