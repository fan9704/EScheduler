from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict  # 添加 ConfigDict 導入
from enum import Enum


class ScheduleType(str, Enum):
    """排程類型枚舉"""
    CRON = "cron"
    RATE = "rate"


class TimeUnit(str, Enum):
    """時間單位枚舉"""
    SECOND = "second"
    SECONDS = "seconds"
    MINUTE = "minute"
    MINUTES = "minutes"
    HOUR = "hour"
    HOURS = "hours"
    DAY = "day"
    DAYS = "days"


class CronField(str, Enum):
    """Cron 欄位枚舉"""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    MONTH = "month"
    WEEKDAY = "weekday"


class RateExpressionRequest(BaseModel):
    """Rate 表達式生成請求"""
    value: int = Field(
        ..., 
        ge=1, 
        description="時間間隔數值",
        examples=[30]
    )
    unit: TimeUnit = Field(
        ..., 
        description="時間單位",
        examples=["seconds"]
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "value": 30,
                    "unit": "seconds",
                    "description": "每30秒執行一次"
                },
                {
                    "value": 5,
                    "unit": "minutes",
                    "description": "每5分鐘執行一次"
                },
                {
                    "value": 1,
                    "unit": "hour",
                    "description": "每小時執行一次"
                },
                {
                    "value": 2,
                    "unit": "days",
                    "description": "每2天執行一次"
                }
            ]
        }
    )


class CronExpressionRequest(BaseModel):
    """Cron 表達式生成請求"""
    minute: str = Field(
        "*", 
        description="分鐘 (0-59)",
        examples=["0"]
    )
    hour: str = Field(
        "*", 
        description="小時 (0-23)",
        examples=["9"]
    )
    day: str = Field(
        "*", 
        description="日 (1-31)",
        examples=["*"]
    )
    month: str = Field(
        "*", 
        description="月 (1-12)",
        examples=["*"]
    )
    weekday: str = Field(
        "*", 
        description="星期 (0-7, 0和7都是週日)",
        examples=["1-5"]
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "minute": "0",
                    "hour": "9",
                    "day": "*",
                    "month": "*",
                    "weekday": "1-5",
                    "description": "工作日早上9點執行"
                },
                {
                    "minute": "30",
                    "hour": "*/2",
                    "day": "*",
                    "month": "*",
                    "weekday": "*",
                    "description": "每2小時的第30分鐘執行"
                },
                {
                    "minute": "0",
                    "hour": "0",
                    "day": "1",
                    "month": "*",
                    "weekday": "*",
                    "description": "每月1號午夜執行"
                },
                {
                    "minute": "0",
                    "hour": "2",
                    "day": "*",
                    "month": "*",
                    "weekday": "0",
                    "description": "每週凌晨2點執行"
                }
            ]
        }
    )


class QuickScheduleRequest(BaseModel):
    """快速排程請求"""
    type: str = Field(
        ..., 
        description="快速排程類型",
        examples=["custom_time"]
    )
    time: Optional[str] = Field(
        None, 
        description="時間 (HH:MM 格式)",
        examples=["09:30"]
    )
    weekdays: Optional[List[int]] = Field(
        None, 
        description="星期幾 (0-6)",
        examples=[[1, 2, 3, 4, 5]]
    )
    interval: Optional[int] = Field(
        None, 
        description="間隔數值",
        examples=[15]
    )
    unit: Optional[str] = Field(
        None, 
        description="間隔單位",
        examples=["minutes"]
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "every_5_minutes",
                    "description": "使用預設模板：每5分鐘執行"
                },
                {
                    "type": "workdays_9am",
                    "description": "使用預設模板：工作日早上9點執行"
                },
                {
                    "type": "custom_time",
                    "time": "09:30",
                    "weekdays": [1, 2, 3, 4, 5],
                    "description": "自定義時間：工作日早上9:30執行"
                },
                {
                    "type": "custom_interval",
                    "interval": 15,
                    "unit": "minutes",
                    "description": "自定義間隔：每15分鐘執行"
                }
            ]
        }
    )


class ScheduleExpressionResponse(BaseModel):
    """排程表達式回應"""
    expression: str = Field(
        ..., 
        description="生成的排程表達式",
        examples=["cron(0 9 * * 1-5)"]
    )
    type: ScheduleType = Field(
        ..., 
        description="表達式類型",
        examples=["cron"]
    )
    description: str = Field(
        ..., 
        description="表達式說明",
        examples=["每天9:00 週一到週五"]
    )
    next_runs: List[str] = Field(
        ..., 
        description="接下來的執行時間",
        examples=[[
            "2024-01-16 09:00:00",
            "2024-01-17 09:00:00",
            "2024-01-18 09:00:00",
            "2024-01-19 09:00:00",
            "2024-01-22 09:00:00"
        ]]
    )


class ScheduleValidationRequest(BaseModel):
    """排程表達式驗證請求"""
    expression: str = Field(
        ..., 
        description="要驗證的排程表達式",
        examples=["cron(0 9 * * 1-5)"]
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "expression": "cron(0 9 * * 1-5)",
                    "description": "驗證工作日早上9點的Cron表達式"
                },
                {
                    "expression": "rate(5 minutes)",
                    "description": "驗證每5分鐘的Rate表達式"
                },
                {
                    "expression": "rate(30 seconds)",
                    "description": "驗證每30秒的Rate表達式"
                },
                {
                    "expression": "cron(*/15 * * * *)",
                    "description": "驗證每15分鐘的Cron表達式"
                },
                {
                    "expression": "invalid_expression",
                    "description": "測試無效表達式的驗證"
                }
            ]
        }
    )


class ScheduleValidationResponse(BaseModel):
    """排程表達式驗證回應"""
    valid: bool = Field(
        ..., 
        description="是否有效",
        examples=[True]
    )
    type: Optional[ScheduleType] = Field(
        None, 
        description="表達式類型",
        examples=["cron"]
    )
    description: Optional[str] = Field(
        None, 
        description="表達式說明",
        examples=["每天9:00 週一到週五"]
    )
    error: Optional[str] = Field(
        None, 
        description="錯誤訊息",
        examples=[None]
    )
    next_runs: Optional[List[str]] = Field(
        None, 
        description="接下來的執行時間",
        examples=[[
            "2024-01-16 09:00:00",
            "2024-01-17 09:00:00",
            "2024-01-18 09:00:00"
        ]]
    )


class ScheduleTemplateResponse(BaseModel):
    """排程模板回應"""
    name: str = Field(
        ..., 
        description="模板名稱",
        examples=["工作日早上9點"]
    )
    description: str = Field(
        ..., 
        description="模板說明",
        examples=["週一到週五早上9點執行"]
    )
    expression: str = Field(
        ..., 
        description="排程表達式",
        examples=["cron(0 9 * * 1-5)"]
    )
    type: ScheduleType = Field(
        ..., 
        description="表達式類型",
        examples=["cron"]
    )
    category: str = Field(
        ..., 
        description="模板分類",
        examples=["工作日排程"]
    )


class CronHelpResponse(BaseModel):
    """Cron 幫助回應"""
    field: CronField = Field(
        ..., 
        description="欄位名稱",
        examples=["minute"]
    )
    description: str = Field(
        ..., 
        description="欄位說明",
        examples=["分鐘"]
    )
    range: str = Field(
        ..., 
        description="取值範圍",
        examples=["0-59"]
    )
    special_chars: List[str] = Field(
        ..., 
        description="特殊字符",
        examples=[["*", ",", "-", "/"]]
    )
    examples: List[Dict[str, str]] = Field(
        ..., 
        description="範例",
        examples=[[
            {"value": "*", "description": "每分鐘"},
            {"value": "0", "description": "第0分鐘"},
            {"value": "*/5", "description": "每5分鐘"}
        ]]
    )