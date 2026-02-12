import unittest
from unittest.mock import patch, AsyncMock
from src.services.execution_strategies.webhook_strategy import WebhookExecutionStrategy
from src.models.pydantic.strategy import ExecutionResult


class TestWebhookExecutionStrategy(unittest.IsolatedAsyncioTestCase):
    """Webhook 執行策略測試"""

    async def asyncSetUp(self):
        self.strategy = WebhookExecutionStrategy()

    async def test_validate_input(self):
        """驗證 URL 格式檢查"""
        self.assertTrue(self.strategy.validate_input("https://example.com", {}))
        self.assertFalse(self.strategy.validate_input("ftp://example.com", {}))
        self.assertFalse(self.strategy.validate_input("", {}))

    async def test_execute_invalid_input(self):
        """無效 URL 應立即返回錯誤"""
        result = await self.strategy.execute("invalid_url", {})
        self.assertIsInstance(result, ExecutionResult)
        self.assertFalse(result.success)
        self.assertIn("無效的 Webhook 參數", result.message)

    @patch("aiohttp.ClientSession")
    async def test_execute_success(self, mock_session_class):
        """模擬 Webhook 呼叫成功情境"""

        # 模擬 response
        mock_response = AsyncMock()
        mock_response.status = 200  # 必須是 int
        mock_response.text = AsyncMock(return_value='{"ok": true}')
        mock_response.url = "https://example.com"
        mock_response.headers = {"Content-Type": "application/json"}

        # 模擬 session.request coroutine 返回 response
        mock_session = AsyncMock()
        mock_session.request = AsyncMock(return_value=mock_response)

        # 模擬 ClientSession async context manager
        mock_session_class.return_value.__aenter__.return_value = mock_session
        mock_session_class.return_value.__aexit__.return_value = None

        target_arn = "https://example.com/webhook"
        target_input = {"method": "POST", "body": {"hello": "world"}}

        result = await self.strategy.execute(target_arn, target_input)

        self.assertTrue(result.success)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data.method, "POST")
        self.assertFalse(result.data.has_signature)
        self.assertIn("Webhook 調用成功", result.message)

    @patch("aiohttp.ClientSession")
    async def test_execute_with_secret(self, mock_session_class):
        """測試含 secret 的簽名 header 是否生成"""
        # 模擬 response
        mock_response = AsyncMock()
        mock_response.status = 200  # 必須是 int
        mock_response.text = AsyncMock(return_value='{"ok": true}')
        mock_response.url = "https://example.com"
        mock_response.headers = {"Content-Type": "application/json"}

        # 模擬 session.request coroutine 返回 response
        mock_session = AsyncMock()
        mock_session.request = AsyncMock(return_value=mock_response)

        # 模擬 ClientSession async context manager
        mock_session_class.return_value.__aenter__.return_value = mock_session
        mock_session_class.return_value.__aexit__.return_value = None

        target_arn = "https://example.com/hook"
        target_input = {"method": "POST", "body": {"data": 1}, "secret": "my_secret"}

        result = await self.strategy.execute(target_arn, target_input)

        self.assertTrue(result.success)
        self.assertTrue(result.data.has_signature)
        self.assertEqual(result.status_code, 200)

    @patch("aiohttp.ClientSession")
    async def test_execute_failure_response(self, mock_session_class):
        """模擬非 2xx 回應"""
        # 模擬 response
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value='{"error": "server error"}')
        mock_response.url = "https://example.com"
        mock_response.headers = {}

        # 模擬 session.request coroutine 返回 response
        mock_session = AsyncMock()
        mock_session.request = AsyncMock(return_value=mock_response)

        # 模擬 ClientSession async context manager
        mock_session_class.return_value.__aenter__.return_value = mock_session
        mock_session_class.return_value.__aexit__.return_value = None

        result = await self.strategy.execute("https://example.com", {"body": {"x": 1}})

        self.assertFalse(result.success)
        self.assertEqual(result.status_code, 500)
        self.assertIn("Webhook 調用失敗", result.message)

    @patch("aiohttp.ClientSession", side_effect=Exception("Network error"))
    async def test_execute_exception(self, mock_session_class):
        """模擬例外情況（如連線錯誤）"""
        result = await self.strategy.execute("https://example.com", {"body": {"x": 1}})
        self.assertFalse(result.success)
        self.assertIn("Webhook 調用失敗", result.message)
