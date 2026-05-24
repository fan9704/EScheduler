import aio_pika
import asyncio
import json
from typing import Dict, Any
from . import ExecutionStrategy
from src.models.pydantic.strategy import ExecutionResult, RabbitMQResult
from src.configs.strategy_config import get_rabbitmq_config
from src.utils.logger import logger


class RabbitMQExecutionStrategy(ExecutionStrategy):
    """RabbitMQ 訊息發送執行策略（支援 Exchange Type / Queue / 優先級 / 死信）"""

    def __init__(self):
        # 從統一配置系統載入 RabbitMQ 配置
        rabbitmq_config = get_rabbitmq_config()

        self.connection_url = rabbitmq_config.connection_url
        self.connection = None

        logger.info(
            f"RabbitMQExecutionStrategy 初始化完成 - URL: {self.connection_url}"
        )

    async def execute(
        self, target_arn: str, target_input: Dict[str, Any]
    ) -> ExecutionResult:
        """發送 RabbitMQ 訊息"""
        start_time = asyncio.get_event_loop().time()

        try:
            if not self.validate_input(target_arn, target_input):
                return ExecutionResult(
                    success=False, message="無效的 RabbitMQ 參數", execution_time=0.0
                )

            # 基本參數
            queue_name = target_arn
            exchange_name = target_input.get("exchange", "")
            routing_key = target_input.get("routing_key", target_arn)
            message_body = target_input.get("message", {})
            message_properties = target_input.get("properties", {})
            is_persistent = target_input.get("is_persistent", True)

            # 進階參數
            queue_args = target_input.get("queue_args", {})
            ttl = target_input.get("ttl")
            priority = target_input.get("priority")
            exchange_type_str: str = target_input.get(
                "exchange_type", "direct"
            )  # 預設 direct

            # 轉換 exchange_type
            exchange_type = getattr(
                aio_pika.ExchangeType,
                exchange_type_str.upper(),
                aio_pika.ExchangeType.DIRECT,
            )

            logger.info(
                f"發送 RabbitMQ 訊息到: {target_arn}, exchange_type={exchange_type_str}"
            )

            # 建立連接
            connection = await aio_pika.connect_robust(self.connection_url)

            try:
                channel = await connection.channel()

                # 設定消息屬性
                properties = {
                    "delivery_mode": aio_pika.DeliveryMode.PERSISTENT
                    if (is_persistent)
                    else aio_pika.DeliveryMode.NOT_PERSISTENT
                }
                properties.update(message_properties)
                if ttl:
                    properties["expiration"] = int(ttl)
                if priority is not None:
                    properties["priority"] = priority

                message = aio_pika.Message(
                    json.dumps(message_body).encode("utf-8"), **properties
                )

                # 發送到 Exchange
                if exchange_name:
                    try:
                        exchange = await channel.get_exchange(exchange_name)
                    except Exception:
                        exchange = await channel.declare_exchange(
                            exchange_name, exchange_type, durable=True
                        )

                    await exchange.publish(message, routing_key=routing_key)
                    target_info = f"Exchange: {exchange_name} ({exchange_type_str}), Routing Key: {routing_key}"

                # 沒指定 Exchange → Queue
                else:
                    await channel.declare_queue(
                        queue_name, durable=True, arguments=queue_args
                    )
                    await channel.default_exchange.publish(
                        message, routing_key=queue_name
                    )
                    target_info = f"Queue: {queue_name}"

                execution_time = asyncio.get_event_loop().time() - start_time
                rabbit_mq_result = RabbitMQResult(
                    target=target_info,
                    message_body=message_body,
                    properties=properties,
                    queue_args=queue_args,
                    message_size=len(json.dumps(message_body)),
                )

                return ExecutionResult(
                    success=True,
                    message="RabbitMQ 訊息發送成功",
                    data=rabbit_mq_result,
                    execution_time=execution_time,
                )

            finally:
                await connection.close()

        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            print(f"RabbitMQ 發送失敗: {str(e)}")
            return ExecutionResult(
                success=False,
                message=f"RabbitMQ 訊息發送失敗: {str(e)}",
                data=None,
                execution_time=execution_time,
            )

    def get_strategy_name(self) -> str:
        return "RabbitMQ"

    def validate_input(self, target_arn: str, target_input: Dict[str, Any]) -> bool:
        """驗證 RabbitMQ 參數"""
        return bool(target_arn)
