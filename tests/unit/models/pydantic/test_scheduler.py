import pytest
from pydantic import ValidationError

from src.models.pydantic.scheduler import ScheduledTaskCreate, TargetType


# -------------------------
# ScheduledTaskCreate validator
# -------------------------
def test_schedule_expression_valid_cron():
    task = ScheduledTaskCreate(
        name="Task Cron",
        schedule_expression="cron(* * * * *)",
        timezone="Asia/Taipei",
        target_type=TargetType.HTTP,
        target_arn="arn:aws:lambda:region:account:function:test",
        recipients=[],  # 你模型可能不需要，但保持一致
    )
    assert task.schedule_expression.startswith("cron(")


def test_schedule_expression_valid_rate():
    task = ScheduledTaskCreate(
        name="Task Rate",
        schedule_expression="rate(5 minutes)",
        timezone="Asia/Taipei",
        target_type=TargetType.HTTP,
        target_arn="arn:aws:lambda:region:account:function:test",
    )
    assert task.schedule_expression.startswith("rate(")


def test_schedule_expression_invalid():
    with pytest.raises(ValidationError) as exc_info:
        ScheduledTaskCreate(
            name="Invalid Task",
            schedule_expression="every minute",  # 非法格式
            timezone="Asia/Taipei",
            target_type=TargetType.HTTP,
            target_arn="arn:aws:lambda:region:account:function:test",
        )
    assert "排程表達式必須是 cron(expression) 或 rate(expression) 格式" in str(
        exc_info.value
    )
