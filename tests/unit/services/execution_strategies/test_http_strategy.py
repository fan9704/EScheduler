import unittest
from unittest.mock import patch, AsyncMock
from src.services.execution_strategies.http_strategy import HttpExecutionStrategy
from src.models.pydantic.strategy import ExecutionResult


class TestHttpExecutionStrategy(unittest.IsolatedAsyncioTestCase):
    """HTTP 執行策略測試"""

    async def asyncSetUp(self):
        self.strategy = HttpExecutionStrategy()

    async def test_validate_input(self):
        """驗證 URL 與 method"""
        self.assertTrue(self.strategy.validate_input("https://example.com", {"method": "GET"}))
        self.assertFalse(self.strategy.validate_input("ftp://example.com", {"method": "GET"}))
        self.assertFalse(self.strategy.validate_input("", {"method": "GET"}))
        self.assertFalse(self.strategy.validate_input("https://example.com", {"method": "FOO"}))

    @patch("aiohttp.ClientSession")
    async def test_execute_success(self, mock_session_class):
        """模擬 HTTP 請求成功"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"ok": true}')
        mock_response.url = "https://example.com"
        mock_response.headers = {"Content-Type": "application/json"}

        mock_session = AsyncMock()
        mock_session.request = AsyncMock(return_value=mock_response)
        mock_session_class.return_value.__aenter__.return_value = mock_session

        target_arn = "https://example.com/api"
        target_input = {"method": "GET", "params": {"q": "test"}}

        result = await self.strategy.execute(target_arn, target_input)

        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data.method, "GET")
        self.assertEqual(result.data.request_params, {"q": "test"})

    @patch("aiohttp.ClientSession")
    async def test_execute_failure_response(self, mock_session_class):
        """模擬非 2xx 回應"""
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value='{"error": "server error"}')
        mock_response.url = "https://example.com"
        mock_response.headers = {}

        mock_session = AsyncMock()
        mock_session.request = AsyncMock(return_value=mock_response)
        mock_session_class.return_value.__aenter__.return_value = mock_session

        result = await self.strategy.execute("https://example.com/api", {"method": "GET"})

        self.assertFalse(result.success)
        self.assertEqual(result.status_code, 500)
        self.assertIn("HTTP GET 請求失敗", result.message)

    @patch("aiohttp.ClientSession", side_effect=Exception("Network error"))
    async def test_execute_exception(self, mock_session_class):
        """模擬連線例外"""
        result = await self.strategy.execute("https://example.com/api", {"method": "GET"})
        self.assertFalse(result.success)
        self.assertIn("HTTP 請求異常", result.message)
