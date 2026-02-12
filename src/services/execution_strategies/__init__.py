from abc import ABC, abstractmethod
from typing import Dict, Any
from src.models.pydantic.strategy import ExecutionResult


class ExecutionStrategy(ABC):
    """執行策略抽象基類"""

    @abstractmethod
    async def execute(
        self, target_arn: str, target_input: Dict[str, Any]
    ) -> ExecutionResult:
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
