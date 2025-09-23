from tortoise import fields, models
from src.models.enum.scheduler import TaskState, TargetType, ExecutionStatus


class ScheduledTask(models.Model):
    """排程任務模型"""
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=255, unique=True, description="任務名稱")
    description = fields.TextField(null=True, description="任務描述")
    
    # 排程相關
    schedule_expression = fields.CharField(max_length=255, description="排程表達式 (cron 或 rate)")
    timezone = fields.CharField(max_length=50, default="Asia/Taipei", description="時區")
    
    # 目標相關 - 使用 TargetType Enum
    target_type = fields.CharEnumField(TargetType, description="目標類型")
    target_arn = fields.CharField(max_length=500, description="目標 ARN 或 URL")
    target_input = fields.JSONField(null=True, description="目標輸入參數")
    
    # 狀態管理 - 使用 TaskState Enum
    state = fields.CharEnumField(TaskState, default=TaskState.ENABLED, description="任務狀態")
    last_execution_time = fields.DatetimeField(null=True, description="最後執行時間")
    next_execution_time = fields.DatetimeField(null=True, description="下次執行時間")
    execution_count = fields.IntField(default=0, description="執行次數")
    
    # 重試和錯誤處理
    max_retry_attempts = fields.IntField(default=3, description="最大重試次數")
    retry_policy = fields.JSONField(null=True, description="重試策略")
    dead_letter_config = fields.JSONField(null=True, description="死信佇列配置")
    
    # 時間戳
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "scheduled_tasks"
        
    def __str__(self):
        return f"ScheduledTask({self.name})"


class TaskExecution(models.Model):
    """任務執行記錄模型"""
    id = fields.IntField(primary_key=True)
    # 修復外鍵引用 - 使用正確的應用名稱格式
    task = fields.ForeignKeyField("models.ScheduledTask", related_name="executions")
    
    # 執行狀態 - 使用 ExecutionStatus Enum
    status = fields.CharEnumField(ExecutionStatus, description="執行狀態")
    started_at = fields.DatetimeField(description="開始時間")
    completed_at = fields.DatetimeField(null=True, description="完成時間")
    
    # 執行結果
    response_code = fields.IntField(null=True, description="回應代碼")
    response_body = fields.TextField(null=True, description="回應內容")
    error_message = fields.TextField(null=True, description="錯誤訊息")
    
    # 重試相關
    attempt_number = fields.IntField(default=1, description="嘗試次數")
    
    class Meta:
        table = "task_executions"
        
    def __str__(self):
        return f"TaskExecution({self.task.name} - {self.status})"