import logging
import asyncio
from typing import Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
from croniter import croniter

from src.services.execution_strategies.strategy_factory import ExecutionStrategyFactory
from src.repositories.scheduler import ScheduledTaskRepository
from src.dependencies.repositories import get_scheduled_task_repository

logger = logging.getLogger(__name__)


class SchedulerEngine:
    """排程引擎服務"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.task_repository: ScheduledTaskRepository = get_scheduled_task_repository()
        self.strategy_factory = ExecutionStrategyFactory()
        self.is_running = False
    
    async def start(self):
        """啟動排程引擎"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("排程引擎已啟動")
            
            # 載入現有任務
            await self.load_existing_tasks()
    
    async def stop(self):
        """停止排程引擎"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("排程引擎已停止")
    
    async def load_existing_tasks(self):
        """載入現有的啟用任務到排程引擎"""
        try:
            print("開始載入既有工作")
            enabled_tasks = await self.task_repository.get_tasks_by_state("ENABLED")
            for task in enabled_tasks:
                await self.add_job(task.id, task.schedule_expression, {
                    'id': task.id,
                    'name': task.name,
                    'target_type': task.target_type,
                    'target_arn': task.target_arn,
                    'target_input': task.target_input
                })
            logger.info(f"已載入 {len(enabled_tasks)} 個啟用任務")
        except Exception as e:
            logger.error(f"載入現有任務失敗: {e}")
    
    async def add_job(self, task_id: int, schedule_expression: str, task_data: Dict[str, Any]):
        """添加任務到排程引擎"""
        try:
            job_id = f"task_{task_id}"
            
            # 解析排程表達式
            trigger = self._parse_schedule_expression(schedule_expression)
            
            # 添加任務
            self.scheduler.add_job(
                func=self._execute_task,
                trigger=trigger,
                id=job_id,
                args=[task_data],
                replace_existing=True,
                max_instances=1
            )
            
            logger.info(f"任務 {task_id} 已添加到排程引擎")
            
        except Exception as e:
            logger.error(f"添加任務 {task_id} 到排程引擎失敗: {e}")
    
    async def remove_job(self, task_id: int):
        """從排程引擎移除任務"""
        try:
            job_id = f"task_{task_id}"
            self.scheduler.remove_job(job_id)
            logger.info(f"任務 {task_id} 已從排程引擎移除")
        except Exception as e:
            logger.error(f"移除任務 {task_id} 失敗: {e}")
    
    async def _execute_task(self, task_data: Dict[str, Any]):
        """執行任務"""
        task_id = task_data['id']
        task_name = task_data['name']
        
        try:
            logger.info(f"自動執行任務: {task_name} (ID: {task_id})")
            
            # 創建執行策略
            strategy = self.strategy_factory.create_strategy(task_data['target_type'])
            
            # 執行任務
            result = await strategy.execute(
                task_data['target_arn'], 
                task_data.get('target_input', {})
            )
            
            # 更新執行記錄
            await self._update_execution_record(task_id, result)
            
            if result.success:
                logger.info(f"任務 {task_name} 自動執行成功")
            else:
                logger.error(f"任務 {task_name} 自動執行失敗: {result.message}")
                
        except Exception as e:
            logger.error(f"任務 {task_id} 執行異常: {e}")
    
    async def _update_execution_record(self, task_id: int, result):
        """更新任務執行記錄"""
        try:
            # 更新執行次數
            await self.task_repository.increment_execution_count(task_id)
            
            # 更新最後執行時間
            from zoneinfo import ZoneInfo
            current_time = datetime.now(ZoneInfo("Asia/Taipei"))
            await self.task_repository.update_execution_time(task_id, current_time)
            
        except Exception as e:
            logger.error(f"更新執行記錄失敗: {e}")
    
    def _parse_schedule_expression(self, schedule_expression: str):
        """解析排程表達式為 APScheduler 觸發器"""
        if schedule_expression.startswith('cron(') and schedule_expression.endswith(')'):
            # Cron 表達式
            cron_expr = schedule_expression[5:-1]
            parts = cron_expr.split()
            if len(parts) == 5:
                minute, hour, day, month, day_of_week = parts
                return CronTrigger(
                    minute=minute,
                    hour=hour,
                    day=day,
                    month=month,
                    day_of_week=day_of_week,
                    timezone="Asia/Taipei"
                )
        
        elif schedule_expression.startswith('rate(') and schedule_expression.endswith(')'):
            # Rate 表達式 - 新增秒級支援
            rate_expr = schedule_expression[5:-1]
            import re
            match = re.match(r'(\d+)\s+(second|seconds|minute|minutes|hour|hours|day|days)', rate_expr)
            if match:
                value, unit = match.groups()
                value = int(value)
                
                if unit.startswith('second'):
                    return IntervalTrigger(seconds=value)
                elif unit.startswith('minute'):
                    return IntervalTrigger(minutes=value)
                elif unit.startswith('hour'):
                    return IntervalTrigger(hours=value)
                elif unit.startswith('day'):
                    return IntervalTrigger(days=value)
        
        raise ValueError(f"無法解析排程表達式: {schedule_expression}")


# 全局排程引擎實例
scheduler_engine = SchedulerEngine()