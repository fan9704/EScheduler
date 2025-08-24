from datetime import datetime
from zoneinfo import ZoneInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from typing import Dict, Any, Optional, List
import re
import threading

from src.repositories.scheduler import ScheduledTaskRepository, TaskExecutionRepository
from src.services.execution_strategies.strategy_factory import ExecutionStrategyFactory
from src.models.enum.scheduler import ExecutionStatus
from src.utils.logger import logger
from src.dependencies.repositories import get_scheduled_task_repository, get_task_execution_repository


class SchedulerEngine:
    """排程引擎服務 (Singleton)"""
    
    _instance: Optional['SchedulerEngine'] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'SchedulerEngine':
        """確保只創建一個實例"""
        if cls._instance is None:
            with cls._lock:
                # 雙重檢查鎖定模式
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化（只執行一次）"""
        if self._initialized:
            return
            
        self.scheduler = AsyncIOScheduler()
        self.task_repository: ScheduledTaskRepository = get_scheduled_task_repository()
        self.execution_repository: TaskExecutionRepository = get_task_execution_repository()
        self.strategy_factory = ExecutionStrategyFactory()
        self.is_running = False
        self._initialized = True
        
        logger.info("SchedulerEngine Singleton 實例已創建")

    @classmethod
    def get_instance(cls) -> 'SchedulerEngine':
        """獲取單例實例"""
        return cls()

    def _get_timezone_aware_now(self, timezone: str = "Asia/Taipei") -> datetime:
        """獲取帶時區的當前時間"""
        tz = ZoneInfo(timezone)
        return datetime.now(tz)

    async def start(self):
        """啟動排程引擎"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("排程引擎已啟動")
            
            # 載入現有任務
            await self.load_existing_tasks()
        else:
            logger.warning("排程引擎已經在運行中")

    async def stop(self):
        """停止排程引擎"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("排程引擎已停止")
        else:
            logger.warning("排程引擎已經停止")
    
    async def load_existing_tasks(self):
        """載入現有的啟用任務到排程引擎"""
        try:
            logger.info("開始載入既有工作")
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
            
            # 檢查任務是否已存在
            if self.scheduler.get_job(job_id):
                logger.info(f"任務 {task_id} 已存在，將替換現有任務")
            
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
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
                logger.info(f"任務 {task_id} 已從排程引擎移除")
            else:
                logger.warning(f"任務 {task_id} 不存在於排程引擎中")
        except Exception as e:
            logger.error(f"移除任務 {task_id} 失敗: {e}")

    def get_job_status(self, task_id: int) -> Dict[str, Any]:
        """獲取任務狀態"""
        job_id = f"task_{task_id}"
        job = self.scheduler.get_job(job_id)
        
        if job:
            return {
                'exists': True,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            }
        else:
            return {'exists': False}

    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """獲取所有任務狀態"""
        jobs = self.scheduler.get_jobs()
        return [
            {
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            }
            for job in jobs
        ]

    async def _execute_task(self, task_data: Dict[str, Any]):
        """執行任務"""
        task_id = task_data['id']
        task_name = task_data['name']
        
        # 創建執行記錄 - 使用帶時區的時間
        execution_id = None
        start_time = self._get_timezone_aware_now()
        
        try:
            logger.info(f"自動執行任務: {task_name} (ID: {task_id})")
            
            # 創建 TaskExecution 記錄
            execution_record = await self.execution_repository.create(
                task_id=task_id,
                status=ExecutionStatus.RUNNING,
                started_at=start_time,
                attempt_number=1
            )
            execution_id = execution_record.id
            
            # 創建執行策略
            strategy = self.strategy_factory.create_strategy(task_data['target_type'])
            
            # 執行任務
            result = await strategy.execute(
                task_data['target_arn'], 
                task_data.get('target_input', {})
            )
            
            # 更新執行記錄
            await self._update_execution_record(task_id, result, execution_id)
            
            if result.success:
                logger.info(f"任務 {task_name} 自動執行成功")
            else:
                logger.error(f"任務 {task_name} 自動執行失敗: {result.message}")
                
        except Exception as e:
            logger.error(f"任務 {task_id} 執行異常: {e}")
            
            # 更新執行記錄為失敗狀態
            if execution_id:
                await self.execution_repository.update_execution_result(
                    execution_id=execution_id,
                    status=ExecutionStatus.FAILED,
                    error_message=str(e)
                )

    async def _update_execution_record(self, task_id: int, result, execution_id: int = None):
        """更新任務執行記錄"""
        try:
            # 更新 ScheduledTask 的執行統計
            await self.task_repository.increment_execution_count(task_id)
            
            # 更新最後執行時間 - 使用帶時區的時間
            current_time = self._get_timezone_aware_now()
            await self.task_repository.update_execution_time(task_id, current_time)
            
            # 更新 TaskExecution 記錄
            if execution_id:
                status = ExecutionStatus.SUCCEEDED if result.success else ExecutionStatus.FAILED
                await self.execution_repository.update_execution_result(
                    execution_id=execution_id,
                    status=status,
                    response_code=result.status_code,
                    response_body=result.message,
                    error_message=None if result.success else result.message
                )
            
        except Exception as e:
            logger.error(f"更新執行記錄失敗: {e}")

    def _parse_schedule_expression(self, expression: str):
        """解析排程表達式"""
        if expression.startswith('cron(') and expression.endswith(')'):
            cron_expr = expression[5:-1]
            return CronTrigger.from_crontab(cron_expr, timezone='Asia/Taipei')
        
        elif expression.startswith('rate(') and expression.endswith(')'):
            rate_expr = expression[5:-1]
            match = re.match(r'(\d+)\s+(second|seconds|minute|minutes|hour|hours|day|days)', rate_expr)
            if not match:
                raise ValueError("無效的 rate 表達式格式")
            
            value, unit = match.groups()
            value = int(value)
            
            if unit.startswith('second'):
                return IntervalTrigger(seconds=value, timezone='Asia/Taipei')
            elif unit.startswith('minute'):
                return IntervalTrigger(minutes=value, timezone='Asia/Taipei')
            elif unit.startswith('hour'):
                return IntervalTrigger(hours=value, timezone='Asia/Taipei')
            elif unit.startswith('day'):
                return IntervalTrigger(days=value, timezone='Asia/Taipei')
            else:
                raise ValueError(f"不支援的時間單位: {unit}")
        
        else:
            raise ValueError("無效的排程表達式格式")


# 全域實例
scheduler_engine = SchedulerEngine.get_instance()