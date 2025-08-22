import logging
import asyncio
import httpx
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
import re

from src.models.enum.scheduler import ExecutionStatus, TargetType
from src.repositories.scheduler import ScheduledTaskRepository, TaskExecutionRepository
from src.dependencies.repositories import get_scheduled_task_repository, get_task_execution_repository

logger = logging.getLogger(__name__)


class SchedulerEngine:
    """排程引擎 - 負責實際的任務排程和執行"""
    
    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.task_repository: Optional[ScheduledTaskRepository] = None
        self.execution_repository: Optional[TaskExecutionRepository] = None
        self._setup_scheduler()
    
    def _setup_scheduler(self):
        """設置 APScheduler"""
        jobstores = {'default': MemoryJobStore()}
        executors = {'default': AsyncIOExecutor()}
        job_defaults = {'coalesce': False, 'max_instances': 3}
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='Asia/Taipei'
        )
    
    def _init_repositories(self):
        """初始化存儲庫（延遲初始化）"""
        if not self.task_repository:
            self.task_repository = get_scheduled_task_repository()
        if not self.execution_repository:
            self.execution_repository = get_task_execution_repository()
    
    async def start(self):
        """啟動排程器"""
        try:
            self._init_repositories()
            
            if self.scheduler and not self.scheduler.running:
                self.scheduler.start()
                logger.info("排程引擎已啟動")
                await self.load_existing_tasks()
        except Exception as e:
            logger.error(f"啟動排程引擎失敗: {e}")
    
    async def stop(self):
        """停止排程器"""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("排程引擎已停止")
    
    async def load_existing_tasks(self):
        """載入現有的啟用任務到排程器"""
        try:
            if not self.task_repository:
                return
                
            enabled_tasks = await self.task_repository.get_enabled_tasks()
            for task in enabled_tasks:
                task_dict = self._task_to_dict(task)
                await self.add_job(task.id, task.schedule_expression, task_dict)
            logger.info(f"已載入 {len(enabled_tasks)} 個啟用任務")
        except Exception as e:
            logger.error(f"載入現有任務失敗: {e}")
    
    def _task_to_dict(self, task) -> Dict[str, Any]:
        """將任務模型轉換為字典"""
        return {
            'id': task.id,
            'name': task.name,
            'target_type': task.target_type,
            'target_arn': task.target_arn,
            'target_input': task.target_input,
            'max_retry_attempts': task.max_retry_attempts
        }
    
    async def add_job(self, task_id: int, schedule_expression: str, task_data: Dict[str, Any]):
        """添加任務到排程器"""
        try:
            job_id = f"task_{task_id}"
            
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            trigger = self._create_trigger(schedule_expression)
            
            self.scheduler.add_job(
                func=self._execute_task,
                trigger=trigger,
                id=job_id,
                args=[task_id, task_data],
                replace_existing=True
            )
            
            logger.info(f"任務 {task_id} 已添加到排程器")
            
        except Exception as e:
            logger.error(f"添加任務 {task_id} 到排程器失敗: {e}")
    
    async def remove_job(self, task_id: int):
        """從排程器移除任務"""
        try:
            job_id = f"task_{task_id}"
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
                logger.info(f"任務 {task_id} 已從排程器移除")
        except Exception as e:
            logger.error(f"移除任務 {task_id} 失敗: {e}")
    
    async def trigger_job_now(self, task_id: int, task_data: Dict[str, Any]):
        """立即觸發任務執行"""
        try:
            await self._execute_task(task_id, task_data)
            logger.info(f"任務 {task_id} 已手動觸發執行")
        except Exception as e:
            logger.error(f"手動觸發任務 {task_id} 失敗: {e}")
    
    def _create_trigger(self, schedule_expression: str):
        """根據排程表達式創建觸發器"""
        if schedule_expression.startswith('cron(') and schedule_expression.endswith(')'):
            cron_expr = schedule_expression[5:-1]
            parts = cron_expr.split()
            if len(parts) == 5:
                minute, hour, day, month, day_of_week = parts
                return CronTrigger(
                    minute=minute, hour=hour, day=day,
                    month=month, day_of_week=day_of_week,
                    timezone='Asia/Taipei'
                )
        
        elif schedule_expression.startswith('rate(') and schedule_expression.endswith(')'):
            rate_expr = schedule_expression[5:-1]
            match = re.match(r'(\d+)\s+(minute|minutes|hour|hours|day|days)', rate_expr)
            if match:
                value, unit = match.groups()
                value = int(value)
                
                if unit.startswith('minute'):
                    return IntervalTrigger(minutes=value, timezone='Asia/Taipei')
                elif unit.startswith('hour'):
                    return IntervalTrigger(hours=value, timezone='Asia/Taipei')
                elif unit.startswith('day'):
                    return IntervalTrigger(days=value, timezone='Asia/Taipei')
        
        raise ValueError(f"不支援的排程表達式格式: {schedule_expression}")
    
    async def _execute_task(self, task_id: int, task_data: Dict[str, Any]):
        """執行任務的核心邏輯"""
        execution_id = None
        start_time = datetime.now()
        
        try:
            # 創建執行記錄
            execution = await self.execution_repository.create(
                task_id=task_id,
                status=ExecutionStatus.RUNNING,
                started_at=start_time,
                attempt_number=1
            )
            execution_id = execution.id
            
            logger.info(f"開始執行任務 {task_id} (執行ID: {execution_id})")
            
            # 更新任務執行計數
            await self.task_repository.increment_execution_count(task_id)
            
            # 根據目標類型執行任務
            target_type = task_data.get('target_type')
            target_arn = task_data.get('target_arn')
            target_input = task_data.get('target_input', {})
            
            if target_type in [TargetType.HTTP, TargetType.WEBHOOK]:
                result = await self._execute_http_request(target_arn, target_input)
            elif target_type == TargetType.LAMBDA:
                result = await self._execute_lambda_function(target_arn, target_input)
            elif target_type == TargetType.SQS:
                result = await self._send_to_sqs(target_arn, target_input)
            elif target_type == TargetType.EMAIL:
                result = await self._send_email(target_arn, target_input)
            else:
                raise ValueError(f"不支援的目標類型: {target_type}")
            
            # 更新執行結果為成功
            await self.execution_repository.update_execution_result(
                execution_id=execution_id,
                status=ExecutionStatus.SUCCEEDED,
                response_code=result.get('status_code'),
                response_body=result.get('response_body')
            )
            
            logger.info(f"任務 {task_id} 執行成功")
            
        except Exception as e:
            logger.error(f"任務 {task_id} 執行失敗: {e}")
            
            if execution_id:
                await self.execution_repository.update_execution_result(
                    execution_id=execution_id,
                    status=ExecutionStatus.FAILED,
                    error_message=str(e)
                )
    
    async def _execute_http_request(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """執行 HTTP 請求"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            method = payload.get('method', 'POST').upper()
            headers = payload.get('headers', {})
            data = payload.get('data', {})
            
            if method == 'GET':
                response = await client.get(url, headers=headers, params=data)
            elif method == 'POST':
                response = await client.post(url, headers=headers, json=data)
            elif method == 'PUT':
                response = await client.put(url, headers=headers, json=data)
            elif method == 'DELETE':
                response = await client.delete(url, headers=headers)
            else:
                raise ValueError(f"不支援的 HTTP 方法: {method}")
            
            return {
                'status_code': response.status_code,
                'response_body': response.text[:1000]
            }
    
    async def _execute_lambda_function(self, function_arn: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """執行 Lambda 函數（模擬）"""
        logger.info(f"模擬執行 Lambda 函數: {function_arn}")
        return {
            'status_code': 200,
            'response_body': json.dumps({'message': 'Lambda function executed', 'payload': payload})
        }
    
    async def _send_to_sqs(self, queue_url: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """發送訊息到 SQS（模擬）"""
        logger.info(f"模擬發送訊息到 SQS: {queue_url}")
        return {
            'status_code': 200,
            'response_body': json.dumps({'message': 'Message sent to SQS', 'data': message})
        }
    
    async def _send_email(self, email_config: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """發送電子郵件（模擬）"""
        logger.info(f"模擬發送電子郵件: {email_config}")
        return {
            'status_code': 200,
            'response_body': json.dumps({'message': 'Email sent', 'content': content})
        }


# 全域排程引擎實例
scheduler_engine = SchedulerEngine()