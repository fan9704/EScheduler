import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from src.services.execution_strategies.email_strategy import EmailExecutionStrategy
from src.models.pydantic.strategy import ExecutionResult


class TestEmailExecutionStrategy(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.strategy = EmailExecutionStrategy()

    @patch("aiosmtplib.send", new_callable=AsyncMock)
    async def test_send_direct_success(self, mock_send):
        """模擬直接發送成功"""
        mock_send.return_value = None
        target_arn = "test@example.com"
        target_input = {"subject": "測試主題", "body": "測試內容"}

        result: ExecutionResult = await self.strategy.execute(target_arn, target_input)

        self.assertTrue(result.success)
        # TODO: 改變回傳物件 Pydantic 型別
        # self.assertEqual(result.data.recipients, [target_arn])
        # self.assertEqual(result.data["subject"], "測試主題")
        mock_send.assert_awaited_once()

    @patch(
        "aiosmtplib.send", new_callable=AsyncMock, side_effect=Exception("SMTP fail")
    )
    async def test_send_direct_failure(self, mock_send):
        """模擬直接發送失敗"""
        target_arn = "test@example.com"
        target_input = {"subject": "測試主題", "body": "測試內容"}

        result: ExecutionResult = await self.strategy.execute(target_arn, target_input)
        self.assertFalse(result.success)
        self.assertIn("郵件發送失敗", result.message)

    @patch(
        "src.models.tortoise.email_template.EmailTemplate.get_or_none",
        new_callable=AsyncMock,
    )
    @patch("aiosmtplib.send", new_callable=AsyncMock)
    @patch(
        "src.models.tortoise.email_template.EmailTemplateUsage.create",
        new_callable=AsyncMock,
    )
    async def test_send_template_success(
        self, mock_create_usage, mock_send, mock_get_template
    ):
        """模擬使用模板發送成功"""
        template = MagicMock()
        template.subject_template = "Hello {{ name }}"
        template.body_template = "Body {{ name }}"
        template.html_template = "<p>{{ name }}</p>"
        template.default_cc = []
        template.default_bcc = []
        template.default_sender = "noreply@test.com"
        template.validate_variables.return_value = None
        template.name = "Test Template"
        template.id = 1
        template.save = AsyncMock()
        mock_get_template.return_value = template
        mock_send.return_value = None

        mock_usage = MagicMock()
        mock_usage.id = 123
        mock_create_usage.return_value = mock_usage

        target_arn = "test@example.com"
        target_input = {
            "use_template": True,
            "template_id": 1,
            "template_variables": {"name": "KT"},
        }

        result: ExecutionResult = await self.strategy.execute(target_arn, target_input)

        self.assertTrue(result.success)
        # self.assertEqual(result.data["template_id"], 1)
        # self.assertEqual(result.data["usage_record_id"], 123)
        mock_send.assert_awaited_once()
        mock_create_usage.assert_awaited_once()
        template.save.assert_awaited_once()

    async def test_validate_input_invalid_email(self):
        """無效的 Email"""
        target_arn = "invalid_email"
        target_input = {"subject": "abc"}
        self.assertFalse(self.strategy.validate_input(target_arn, target_input))

    async def test_validate_input_template_missing_id(self):
        """模板使用但缺少 template_id"""
        target_arn = "test@example.com"
        target_input = {"use_template": True}
        self.assertFalse(self.strategy.validate_input(target_arn, target_input))
