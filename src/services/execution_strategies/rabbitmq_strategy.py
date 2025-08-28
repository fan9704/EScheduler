import aio_pika
import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any
from . import ExecutionStrategy
from src.models.pydantic.strategy import ExecutionResult

logger = logging.getLogger(__name__)


class RabbitMQExecutionStrategy(ExecutionStrategy):
    """RabbitMQ 訊息發送執行策略（支援 Exchange / Queue / 優先級 / 死信）"""
    
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
            
            # 基本參數解析
            queue_name = target_arn
            exchange_name = target_input.get("exchange", "")
            routing_key = target_input.get("routing_key", target_arn)
            message_body = target_input.get("message", {})
            message_properties = target_input.get("properties", {})

            # 新增進階功能參數
            queue_args = target_input.get("queue_args", {}) # e.g. {"x-max-priority": 10, "x-dead-letter-exchange": "dlx"}
            ttl = target_input.get("ttl")                   # 消息過期時間 (ms)
            priority = target_input.get("priority")         # 消息優先級
            
            logger.info(f"發送 RabbitMQ 訊息到: {target_arn}")
            
            # 建立連接
            connection = await aio_pika.connect_robust(self.connection_url)
            
            try:
                channel = await connection.channel()
                
                # 設定消息屬性
                properties = {
                    "delivery_mode": aio_pika.DeliveryMode.PERSISTENT,  # 預設持久化
                }
                properties.update(message_properties)
                if ttl:
                    properties["expiration"] = int(ttl)
                if priority is not None:
                    properties["priority"] = priority

                message = aio_pika.Message(
                    json.dumps(message_body).encode("utf-8"),
                    **properties
                )

                # 如果指定 Exchange
                if exchange_name:
                    try:
                        exchange = await channel.get_exchange(exchange_name)
                    except Exception:
                        exchange = await channel.declare_exchange(exchange_name, aio_pika.ExchangeType.DIRECT, durable=True)
                    
                    await exchange.publish(message, routing_key=routing_key)
                    target_info = f"Exchange: {exchange_name}, Routing Key: {routing_key}"

                # 如果沒指定 Exchange → 直接 Queue
                else:
                    queue = await channel.declare_queue(queue_name, durable=True, arguments=queue_args)
                    await channel.default_exchange.publish(message, routing_key=queue_name)
                    target_info = f"Queue: {queue_name}"

                execution_time = asyncio.get_event_loop().time() - start_time
                
                return ExecutionResult(
                    success=True,
                    message="RabbitMQ 訊息發送成功",
                    data={
                        "target": target_info,
                        "message_body": message_body,
                        "properties": properties,
                        "queue_args": queue_args,
                        "message_size": len(json.dumps(message_body)),
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
        return bool(target_arn)