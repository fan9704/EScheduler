import pytest
from datetime import datetime, timedelta, timezone
from fastapi import status
from src.models.tortoise.scheduler import ScheduledTask, TaskExecution
from src.models.enum.scheduler import TaskState, TargetType, ExecutionStatus


class TestScheduledTaskModel:
    @pytest.mark.asyncio
    async def test_create_scheduled_task(self, in_memory_db):
        """測試建立 ScheduledTask"""
        task = await ScheduledTask.create(
            name="daily_backup",
            description="每日備份任務",
            schedule_expression="cron(0 3 * * ? *)",
            timezone="Asia/Taipei",
            target_type=TargetType.HTTP,
            target_arn="https://api.example.com/backup",
            target_input={"bucket": "daily-backup"},
            state=TaskState.ENABLED,
            execution_count=5,
            max_retry_attempts=3,
            retry_policy={"strategy": "exponential_backoff"},
            dead_letter_config={"queue_arn": "arn:aws:sqs:dead-letter"},
        )

        assert task.id is not None
        assert task.name == "daily_backup"
        assert task.state == TaskState.ENABLED
        assert task.target_type == TargetType.HTTP
        assert "backup" in task.target_arn
        assert task.retry_policy["strategy"] == "exponential_backoff"
        assert str(task) == "ScheduledTask(daily_backup)"

    @pytest.mark.asyncio
    async def test_task_state_transition(self, in_memory_db):
        """測試任務狀態變化"""
        task = await ScheduledTask.create(
            name="state_test",
            schedule_expression="rate(1 hour)",
            target_type=TargetType.HTTP,
            target_arn="arn:aws:lambda:ap-northeast-1:123456789012:function:test",
            state=TaskState.DISABLED,
        )

        assert task.state == TaskState.DISABLED
        task.state = TaskState.ENABLED
        await task.save()
        fetched = await ScheduledTask.get(id=task.id)
        assert fetched.state == TaskState.ENABLED

    @pytest.mark.asyncio
    async def test_update_execution_times_and_count(self, in_memory_db):
        """測試更新任務執行時間與計數"""
        now = datetime.now(timezone.utc)
        task = await ScheduledTask.create(
            name="update_times",
            schedule_expression="rate(5 minutes)",
            target_type=TargetType.EMAIL,
            target_arn="arn:aws:sqs:ap-northeast-1:123456789012:queue",
        )

        task.last_execution_time = now
        task.next_execution_time = now + timedelta(minutes=5)
        task.execution_count = 10
        await task.save()

        updated = await ScheduledTask.get(id=task.id)
        assert updated.execution_count == 10
        assert abs((updated.next_execution_time - now).total_seconds() - 300) < 1


class TestTaskExecutionModel:
    @pytest.mark.asyncio
    async def test_create_task_execution(self, in_memory_db):
        """測試建立 TaskExecution"""
        task = await ScheduledTask.create(
            name="execution_test",
            schedule_expression="rate(10 minutes)",
            target_type=TargetType.HTTP,
            target_arn="https://example.com/run",
        )

        start_time = datetime.now(timezone.utc)
        exec_record = await TaskExecution.create(
            task=task,
            status=ExecutionStatus.RUNNING,
            started_at=start_time,
            attempt_number=1,
        )

        assert exec_record.id is not None
        assert exec_record.task.id == task.id
        assert exec_record.status == ExecutionStatus.RUNNING
        assert str(exec_record) == f"TaskExecution({task.name} - {ExecutionStatus.RUNNING})"

    @pytest.mark.asyncio
    async def test_complete_task_execution_success(self, in_memory_db):
        """測試任務執行完成狀態"""
        task = await ScheduledTask.create(
            name="success_case",
            schedule_expression="rate(30 minutes)",
            target_type=TargetType.WEBHOOK,
            target_arn="arn:aws:lambda:example:function:test",
        )

        start_time = datetime.now(timezone.utc)
        exec_record = await TaskExecution.create(
            task=task,
            status=ExecutionStatus.SUCCEEDED,
            started_at=start_time,
        )

        exec_record.status = ExecutionStatus.SUCCEEDED
        exec_record.completed_at = start_time + timedelta(seconds=15)
        exec_record.response_code = status.HTTP_200_OK
        exec_record.response_body = '{"message": "ok"}'
        await exec_record.save()

        updated = await TaskExecution.get(id=exec_record.id)
        assert updated.status == ExecutionStatus.SUCCEEDED
        assert updated.response_code == status.HTTP_200_OK
        assert "ok" in updated.response_body

    @pytest.mark.asyncio
    async def test_failed_task_execution_with_retry(self, in_memory_db):
        """測試任務執行失敗並重試"""
        task = await ScheduledTask.create(
            name="fail_case",
            schedule_expression="rate(1 minute)",
            target_type=TargetType.HTTP,
            target_arn="https://example.com/fail",
        )

        start_time = datetime.now(timezone.utc)
        exec_record = await TaskExecution.create(
            task=task,
            status=ExecutionStatus.FAILED,
            started_at=start_time,
            completed_at=start_time,
            response_code=500,
            error_message="Internal Server Error",
            attempt_number=2,
        )

        assert exec_record.status == ExecutionStatus.FAILED
        assert exec_record.response_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Error" in exec_record.error_message
        assert exec_record.attempt_number == 2
