import pytest
from datetime import datetime
from tests.conftest import in_memory_db
from src.models.tortoise.email_template import EmailTemplate, EmailTemplateUsage

class TestEmailTemplateModel:
    @pytest.mark.asyncio
    async def test_create_email_template(self, in_memory_db):
        """測試建立 EmailTemplate"""
        tpl = await EmailTemplate.create(
            name="welcome_email",
            description="Welcome template",
            subject_template="Welcome, {{name}}!",
            body_template="Hello {{name}}",
            html_template="<h1>Hello {{name}}</h1>",
            variables=[
                {"name": "name", "type": "string", "required": True},
                {"name": "age", "type": "number"},
                {"name": "contact", "type": "email"},
            ],
            default_sender="noreply@example.com",
            default_cc=["team@example.com"],
            default_bcc=None,
            is_active=True,
            is_system_template=False,
        )

        assert tpl.id is not None
        assert tpl.name == "welcome_email"
        assert tpl.get_variable_names() == ["name", "age", "contact"]


    @pytest.mark.asyncio
    async def test_validate_variables_success(self, in_memory_db):
        """測試變數驗證通過"""
        tpl = await EmailTemplate.create(
            name="verify_email",
            subject_template="Verify",
            body_template="Hello {{email}}",
            html_template="<p>{{email}}</p>",
            variables=[
                {"name": "email", "type": "email", "required": True},
                {"name": "age", "type": "number"},
            ],
        )

        provided = {"email": "user@example.com", "age": 25}
        errors = tpl.validate_variables(provided)
        assert errors == {}


    @pytest.mark.asyncio
    async def test_validate_variables_missing_required(self, in_memory_db):
        """測試缺少必填變數"""
        tpl = await EmailTemplate.create(
            name="reset_password",
            subject_template="Reset",
            body_template="Hi",
            html_template="<p>Hi</p>",
            variables=[
                {"name": "username", "type": "string", "required": True},
                {"name": "token", "type": "string", "required": True},
            ],
        )

        provided = {"username": "tester"}
        errors = tpl.validate_variables(provided)
        assert "token" in errors
        assert "未提供" in errors["token"]


    @pytest.mark.asyncio
    async def test_validate_variables_invalid_email_and_number(self, in_memory_db):
        """測試錯誤格式 (email / number)"""
        tpl = await EmailTemplate.create(
            name="error_case",
            subject_template="Hi",
            body_template="Hi",
            variables=[
                {"name": "email", "type": "email"},
                {"name": "amount", "type": "number"},
            ],
        )

        provided = {"email": "not-an-email", "amount": "abc"}
        errors = tpl.validate_variables(provided)

        assert "email" in errors
        assert "不是有效的 email 格式" in errors["email"]
        assert "amount" in errors
        assert "必須是數字" in errors["amount"]


    @pytest.mark.asyncio
    async def test_email_template_usage_create(self, in_memory_db):
        """測試 EmailTemplateUsage 建立"""
        tpl = await EmailTemplate.create(
            name="usage_test",
            subject_template="Subject",
            body_template="Body",
            variables=[],
        )

        usage = await EmailTemplateUsage.create(
            template=tpl,
            variables_used={"foo": "bar"},
            rendered_subject="Subject",
            rendered_body="Body",
            rendered_html="<p>Body</p>",
            recipients=["a@example.com"],
            sender="noreply@example.com",
            is_successful=True,
            error_message=None,
        )

        assert usage.id is not None
        assert usage.template.id == tpl.id
        assert usage.is_successful
