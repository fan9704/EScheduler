from typing import Dict, Type, List

from . import ExecutionStrategy
from .http_strategy import HttpExecutionStrategy
from .webhook_strategy import WebhookExecutionStrategy
from .email_strategy import EmailExecutionStrategy
from .rabbitmq_strategy import RabbitMQExecutionStrategy


class ExecutionStrategyFactory:
    """執行策略工廠"""
    
    # 只存儲策略類別，不存儲實例
    _strategies: Dict[str, Type[ExecutionStrategy]] = {
        'http': HttpExecutionStrategy,
        'webhook': WebhookExecutionStrategy,
        'rabbitmq': RabbitMQExecutionStrategy,
        'email': EmailExecutionStrategy,
    }
    
    @classmethod
    def create_strategy(cls, strategy_type: str, **kwargs) -> ExecutionStrategy:
        """創建執行策略實例"""
        strategy_type = strategy_type.lower()
        
        if strategy_type not in cls._strategies:
            raise ValueError(f"不支援的執行策略: {strategy_type}")
        
        strategy_class = cls._strategies[strategy_type]
        # 策略類會在 __init__ 中自動從配置系統載入參數
        return strategy_class(**kwargs)
    
    @classmethod
    def get_supported_strategies(cls) -> List[str]:
        """獲取支援的策略類型列表"""
        return list(cls._strategies.keys())
    
    @classmethod
    def register_strategy(cls, strategy_type: str, strategy_class: Type[ExecutionStrategy]):
        """註冊新的執行策略"""
        cls._strategies[strategy_type.lower()] = strategy_class