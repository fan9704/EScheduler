from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime


class ExecutionResult:
    """執行結果封裝類"""
    def __init__(self, success: bool, message: str, data: Dict[str, Any] = None, 
                 execution_time: float = 0.0, status_code: int = None):
        self.success = success
        self.message = message
        self.data = data or {}
        self.execution_time = execution_time
        self.status_code = status_code
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'message': self.message,
            'data': self.data,
            'execution_time': self.execution_time,
            'status_code': self.status_code,
            'timestamp': self.timestamp.isoformat()
        }


class ExecutionStrategy(ABC):
    """執行策略抽象基類"""
    
    @abstractmethod
    async def execute(self, target_arn: str, target_input: Dict[str, Any]) -> ExecutionResult:
        """執行任務
        
        Args:
            target_arn: 目標地址或標識符
            target_input: 執行參數
            
        Returns:
            ExecutionResult: 執行結果
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """獲取策略名稱"""
        pass
    
    def validate_input(self, target_arn: str, target_input: Dict[str, Any]) -> bool:
        """驗證輸入參數（可選重寫）"""
        return bool(target_arn)