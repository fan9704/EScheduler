from src.services.scheduler_engine import SchedulerEngine

def get_scheduler_engine():
    """獲取排程引擎單例實例"""
    return SchedulerEngine.get_instance()