import aio_pika
import asyncio
import logging
import json
from typing import Dict, Any
from . import ExecutionStrategy, ExecutionResult

logger = logging.getLogger(__name__)


class RabbitMQExecutionStrategy(ExecutionStrategy):
    """RabbitMQ 訊息發送執行策略"""
    
    def __init__(self, connection_url: str = None):
        self.connection_url = connection_url or "amqp://guest:guest@localhost:5672/"
        self.connection = None
    
    async def execute(self, target_arn: str, target_input: Dict[str, Any]) -> ExecutionResult:
        """發送 RabbitMQ 訊息"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            if not self.validate_input(target_arn, target_input):
                return ExecutionResult(
                    success=False,
                    message="無效的 RabbitMQ 參數",
                    execution_time=0.0
                )
            
            # 解析目標 ARN (格式: rabbitmq://exchange/routing_key 或 queue_name)
            queue_name = target_arn
            exchange_name = target_input.get('exchange', '')
            routing_key = target_input.get('routing_key', target_arn)
            message_body = target_input.get('message', {})
            message_properties = target_input.get('properties', {})
            
            logger.info(f"發送 RabbitMQ 訊息到: {target_arn}")
            
            # 建立連接
            connection = await aio_pika.connect_robust(self.connection_url)
            
            try:
                channel = await connection.channel()
                
                if exchange_name:
                    # 發送到 Exchange
                    exchange = await channel.get_exchange(exchange_name)
                    message = aio_pika.Message(
                        json.dumps(message_body).encode('utf-8'),
                        **message_properties
                    )
                    await exchange.publish(message, routing_key=routing_key)
                    target_info = f"Exchange: {exchange_name}, Routing Key: {routing_key}"
                else:
                    # 直接發送到 Queue
                    queue = await channel.declare_queue(queue_name, durable=True)
                    message = aio_pika.Message(
                        json.dumps(message_body).encode('utf-8'),
                        **message_properties
                    )
                    await channel.default_exchange.publish(message, routing_key=queue_name)
                    target_info = f"Queue: {queue_name}"
                
                execution_time = asyncio.get_event_loop().time() - start_time
                
                return ExecutionResult(
                    success=True,
                    message="RabbitMQ 訊息發送成功",
                    data={
                        'target': target_info,
                        'message_body': message_body,
                        'properties': message_properties,
                        'message_size': len(json.dumps(message_body))
                    },
                    execution_time=execution_time
                )
                
            finally:
                await connection.close()
                
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            return ExecutionResult(
                success=False,
                message=f"RabbitMQ 訊息發送失敗: {str(e)}",
                execution_time=execution_time
            )
    
    def get_strategy_name(self) -> str:
        return "RabbitMQ"
    
    def validate_input(self, target_arn: str, target_input: Dict[str, Any]) -> bool:
        """驗證 RabbitMQ 參數"""
        if not target_arn:
            return False
        return True