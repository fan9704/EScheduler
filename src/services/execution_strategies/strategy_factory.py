from typing import Dict, Type, List
from . import ExecutionStrategy
from .http_strategy import HttpExecutionStrategy


class ExecutionStrategyFactory:
    """執行策略工廠"""
    
    _strategies: Dict[str, Type[ExecutionStrategy]] = {
        'http': HttpExecutionStrategy,
        'webhook': HttpExecutionStrategy,  # 暫時使用 HTTP 策略
    }
    
    @classmethod
    def create_strategy(cls, strategy_type: str, **kwargs) -> ExecutionStrategy:
        """創建執行策略實例"""
        strategy_type = strategy_type.lower()
        
        if strategy_type not in cls._strategies:
            raise ValueError(f"不支援的執行策略: {strategy_type}")
        
        strategy_class = cls._strategies[strategy_type]
        return strategy_class(**kwargs)
    
    @classmethod
    def get_supported_strategies(cls) -> List[str]:
        """獲取支援的策略類型列表"""
        return list(cls._strategies.keys())
    
    @classmethod
    def register_strategy(cls, strategy_type: str, strategy_class: Type[ExecutionStrategy]):
        """註冊新的執行策略"""
        cls._strategies[strategy_type.lower()] = strategy_class