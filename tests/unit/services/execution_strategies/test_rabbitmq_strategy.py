import unittest
from unittest.mock import patch, AsyncMock
from src.services.execution_strategies.rabbitmq_strategy import RabbitMQExecutionStrategy


class TestRabbitMQExecutionStrategy(unittest.IsolatedAsyncioTestCase):
    """RabbitMQ 執行策略測試"""

    async def asyncSetUp(self):
        self.strategy = RabbitMQExecutionStrategy()

    async def test_validate_input(self):
        self.assertTrue(self.strategy.validate_input("my_queue", {}))
        self.assertFalse(self.strategy.validate_input("", {}))

    @patch("aio_pika.connect_robust")
    async def test_execute_success_queue(self, mock_connect):
        """模擬發送訊息到 Queue 成功"""
        mock_connection = AsyncMock()
        mock_channel = AsyncMock()
        mock_default_exchange = AsyncMock()
        mock_connection.channel.return_value = mock_channel
        mock_channel.default_exchange = mock_default_exchange
        mock_connect.return_value = mock_connection

        target_arn = "my_queue"
        target_input = {"message": {"foo": "bar"}}

        result = await self.strategy.execute(target_arn, target_input)

        self.assertTrue(result.success)
        self.assertIn("Queue", result.data.target)
        self.assertEqual(result.data.message_body, {"foo": "bar"})

        mock_channel.default_exchange.publish.assert_awaited_once()

    @patch("aio_pika.connect_robust")
    async def test_execute_success_exchange(self, mock_connect):
        """模擬發送訊息到 Exchange 成功"""
        mock_connection = AsyncMock()
        mock_channel = AsyncMock()
        mock_exchange = AsyncMock()
        mock_channel.get_exchange.side_effect = Exception("not found")
        mock_channel.declare_exchange.return_value = mock_exchange
        mock_connection.channel.return_value = mock_channel
        mock_connect.return_value = mock_connection

        target_arn = "my_queue"
        target_input = {
            "exchange": "my_exchange",
            "exchange_type": "fanout",
            "routing_key": "rk1",
            "message": {"hello": "world"}
        }

        result = await self.strategy.execute(target_arn, target_input)

        self.assertTrue(result.success)
        self.assertIn("Exchange", result.data.target)
        mock_channel.declare_exchange.assert_awaited_once()
        mock_exchange.publish.assert_awaited_once()

    @patch("aio_pika.connect_robust", side_effect=Exception("Connection failed"))
    async def test_execute_connection_exception(self, mock_connect):
        """模擬連線失敗"""
        result = await self.strategy.execute("my_queue", {"message": {"x": 1}})
        self.assertFalse(result.success)
        self.assertIn("RabbitMQ 訊息發送失敗", result.message)
