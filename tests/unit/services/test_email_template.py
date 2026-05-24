# tests/unit/services/test_email_template.py
import datetime as dt
import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from jinja2 import TemplateError

from src.exceptions.exceptions import NotFoundError, ValidationError
from src.models.pydantic.email_template import (
    EmailTemplateCreate,
    EmailTemplatePreview,
    EmailTemplateUpdate,
)
from src.services.email_template import EmailTemplateService


@pytest.mark.asyncio
class TestEmailTemplateService:
    """EmailTemplateService 單元測試"""

    async def async_set_up_service(self):
        return EmailTemplateService()

    async def test_create_template_success(self):
        service = await self.async_set_up_service()

        payload = EmailTemplateCreate(
            name="Test Template",
            description="A test",
            subject_template="Hello {{ name }}",
            body_template="Body {{ name }}",
            html_template="<p>{{ name }}</p>",
            variables=[],
            default_sender="sender@test.com",
            default_cc=[],
            default_bcc=[],
            is_active=True,
        )

        mock_template = SimpleNamespace(
            id=1,
            name=payload.name,
            description=payload.description,
            subject_template=payload.subject_template,
            body_template=payload.body_template,
            html_template=payload.html_template,
            variables=[],
            default_sender=payload.default_sender,
            default_cc=payload.default_cc,
            default_bcc=payload.default_bcc,
            is_active=payload.is_active,
            is_system_template=False,
            usage_count=0,
            last_used_at=None,
            created_at=dt.datetime.now(dt.timezone.utc),
            updated_at=dt.datetime.now(dt.timezone.utc),
        )

        mock_qs = MagicMock()
        mock_qs.first = AsyncMock(return_value=None)  # 模擬模板不存在

        with (
            patch(
                "src.models.tortoise.email_template.EmailTemplate.filter",
                return_value=mock_qs,
            ),
            patch(
                "src.models.tortoise.email_template.EmailTemplate.create",
                new_callable=AsyncMock,
                return_value=mock_template,
            ),
        ):
            result = await service.create_template(payload)

        assert result.id == mock_template.id
        assert result.name == payload.name
        assert result.is_system_template is False

    async def test_create_template_duplicate_name_raises(self):
        service = await self.async_set_up_service()

        payload = EmailTemplateCreate(
            name="Duplicate Template",
            description="Duplicate test",
            subject_template="Subject",
            body_template="Body",
            html_template="<p>HTML</p>",
            variables=[],
            default_sender="sender@test.com",
            default_cc=[],
            default_bcc=[],
            is_active=True,
        )

        mock_existing = SimpleNamespace(id=1, name=payload.name)
        mock_qs = MagicMock()
        mock_qs.first = AsyncMock(return_value=mock_existing)

        with patch(
            "src.models.tortoise.email_template.EmailTemplate.filter",
            return_value=mock_qs,
        ):
            with pytest.raises(ValidationError) as exc_info:
                await service.create_template(payload)

        assert payload.name in str(exc_info.value)

    async def test_preview_template_success(self):
        service = await self.async_set_up_service()

        payload = EmailTemplatePreview(
            subject_template="Hello {{ name }}",
            body_template="Body {{ name }}",
            html_template=None,
            variables={"name": "John"},
        )

        result = await service.preview_template(payload)
        assert result.subject == "Hello John"
        assert "John" in result.body
        assert "name" in result.variables_used

    async def test_preview_template_invalid_syntax_raises(self):
        service = await self.async_set_up_service()

        payload = EmailTemplatePreview(
            subject_template="{% invalid syntax %}",
            body_template="Body",
            html_template=None,
            variables={},
        )

        with pytest.raises(ValidationError):
            await service.preview_template(payload)

    async def test_delete_template_success(self):
        service = await self.async_set_up_service()

        mock_template = AsyncMock()
        # get_or_none 返回 mock_template，並且 mock_template.delete() 應被 await
        with patch(
            "src.models.tortoise.email_template.EmailTemplate.get_or_none",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = mock_template
            result = await service.delete_template(template_id=1)
            assert result is True
            mock_template.delete.assert_awaited_once()

    async def test_delete_template_not_found_raises(self):
        service = await self.async_set_up_service()

        with patch(
            "src.models.tortoise.email_template.EmailTemplate.get_or_none",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = None
            with pytest.raises(NotFoundError):
                await service.delete_template(template_id=1)

    async def test_list_templates_with_filters(self):
        service = await self.async_set_up_service()

        mock_template = SimpleNamespace(
            id=1,
            name="Test Template",
            description="A test",
            subject_template="Hello {{ name }}",
            body_template="Body {{ name }}",
            html_template="<p>{{ name }}</p>",
            variables=[],
            default_sender="sender@test.com",
            default_cc=[],
            default_bcc=[],
            is_active=True,
            is_system_template=False,
            usage_count=0,
            last_used_at=None,
            created_at=dt.datetime.now(dt.timezone.utc),
            updated_at=dt.datetime.now(dt.timezone.utc),
        )
        # 模擬 QuerySet，可鏈式呼叫 filter / order_by / limit / offset
        mock_qs = MagicMock()
        mock_qs.filter.return_value = mock_qs
        mock_qs.order_by.return_value = mock_qs
        mock_qs.limit.return_value = mock_qs
        # offset 是 async (被 await)，所以設定為 AsyncMock 返回 list
        mock_qs.offset = AsyncMock(return_value=[mock_template])

        # EmailTemplate.all() 回傳 mock_qs
        with patch(
            "src.models.tortoise.email_template.EmailTemplate.all", return_value=mock_qs
        ):
            result = await service.list_templates(
                is_active=True, search="Test", limit=10, offset=0
            )

        assert len(result) == 1
        assert result[0].name == "Test Template"

    # -------------------------
    # get_template
    # -------------------------
    async def test_get_template_found(self):
        service = await self.async_set_up_service()
        mock_t = SimpleNamespace(
            id=1,
            name="Test Template",
            description="A test",
            subject_template="Hello {{ name }}",
            body_template="Body {{ name }}",
            html_template="<p>{{ name }}</p>",
            variables=[],
            default_sender="sender@test.com",
            default_cc=[],
            default_bcc=[],
            is_active=True,
            is_system_template=False,
            usage_count=0,
            last_used_at=None,
            created_at=dt.datetime.now(dt.timezone.utc),
            updated_at=dt.datetime.now(dt.timezone.utc),
        )

        with patch(
            "src.models.tortoise.email_template.EmailTemplate.get_or_none",
            AsyncMock(return_value=mock_t),
        ):
            result = await service.get_template(1)

        assert result.name == "Test Template"

    async def test_get_template_not_found_returns_none(self):
        service = await self.async_set_up_service()
        with patch(
            "src.models.tortoise.email_template.EmailTemplate.get_or_none",
            AsyncMock(return_value=None),
        ):
            result = await service.get_template(999)
        assert result is None

    # -------------------------
    # update_template
    # -------------------------
    async def test_update_template_success(self):
        service = await self.async_set_up_service()
        mock_t = SimpleNamespace(
            id=1,
            name="OldName",
            description="A test",
            subject_template="Hello {{ name }}",
            body_template="Body {{ name }}",
            html_template="<p>{{ name }}</p>",
            variables=[],
            default_sender="sender@test.com",
            default_cc=[],
            default_bcc=[],
            is_active=True,
            is_system_template=False,
            usage_count=0,
            last_used_at=None,
            created_at=dt.datetime.now(dt.timezone.utc),
            updated_at=dt.datetime.now(dt.timezone.utc),
        )

        # 模擬 update_from_dict 會把更新資料寫回 mock_t 的屬性
        async def _update_from_dict_side_effect(update_data):
            for k, v in update_data.items():
                setattr(mock_t, k, v)

        mock_t.update_from_dict = AsyncMock(side_effect=_update_from_dict_side_effect)
        mock_t.save = AsyncMock()

        data = EmailTemplateUpdate(name="NewName", description="Updated")
        # 第一次 get_or_none 回傳 mock_t（現有的 template），第二次（檢查是否有同名 template）回傳 None
        with patch(
            "src.models.tortoise.email_template.EmailTemplate.get_or_none",
            AsyncMock(side_effect=[mock_t, None]),
        ):
            result = await service.update_template(1, data)

        assert result.name == "NewName"
        mock_t.update_from_dict.assert_awaited_once()
        mock_t.save.assert_awaited_once()

    async def test_update_template_not_found_raises(self):
        service = await self.async_set_up_service()
        with patch(
            "src.models.tortoise.email_template.EmailTemplate.get_or_none",
            AsyncMock(return_value=None),
        ):
            with pytest.raises(NotFoundError):
                await service.update_template(1, EmailTemplateUpdate(name="X"))

    async def test_update_template_name_conflict_raises(self):
        service = await self.async_set_up_service()
        mock_t = SimpleNamespace(id=1, name="OldName")
        data = EmailTemplateUpdate(name="NewName")
        # 回傳：第一次為 mock_t，第二次檢查同名時回傳一個非 None 的物件 => 觸發 ValidationError
        with patch(
            "src.models.tortoise.email_template.EmailTemplate.get_or_none",
            AsyncMock(side_effect=[mock_t, SimpleNamespace(id=2, name="NewName")]),
        ):
            with pytest.raises(ValidationError):
                await service.update_template(1, data)

    # -------------------------
    # preview_template — 一般例外與 TemplateError
    # -------------------------
    async def test_preview_template_jinja_template_error(self):
        service = await self.async_set_up_service()
        with patch.object(
            service, "_validate_template_syntax", side_effect=TemplateError("invalid")
        ):
            with pytest.raises(ValidationError):
                await service.preview_template(
                    EmailTemplatePreview(
                        subject_template="Hi {{ name }}",
                        body_template="Body {{ name }}",
                        html_template=None,
                        variables={"name": "John"},
                    )
                )

    async def test_preview_template_general_exception(self):
        service = await self.async_set_up_service()
        # 模擬某些意外錯誤，例如 KeyError
        with patch.object(
            service, "_render_template", side_effect=KeyError("Missing var")
        ):
            with pytest.raises(ValidationError) as exc_info:
                await service.preview_template(
                    EmailTemplatePreview(
                        subject_template="Hi {{ name }}",
                        body_template="Body {{ name }}",
                        html_template=None,
                        variables={"name": "John"},
                    )
                )
        assert "預覽失敗" in str(exc_info.value)

    async def test_preview_template_missing_subject_body(self):
        service = await self.async_set_up_service()
        # 缺 subject 或 body，會進入 ValueError 分支
        payload = EmailTemplatePreview(
            subject_template=None, body_template=None, html_template=None, variables={}
        )
        with pytest.raises(ValidationError):
            await service.preview_template(payload)

    # -------------------------
    # get_template_usage_stats
    # -------------------------
    async def test_get_template_usage_stats_success(self):
        service = await self.async_set_up_service()

        mock_t = SimpleNamespace(id=1, name="UsageTemplate")
        mock_usage = [
            SimpleNamespace(used_at=dt.datetime.now(), template_id=1),
            SimpleNamespace(
                used_at=dt.datetime.now() - dt.timedelta(days=1), template_id=1
            ),
        ]

        # 假裝 EmailTemplate.get_or_none 回傳模板
        # EmailTemplateUsage.filter(...) 回傳一個物件，其 .all() 為 AsyncMock -> 回傳 mock_usage
        mock_usage_qs = MagicMock()
        mock_usage_qs.all = AsyncMock(return_value=mock_usage)

        with (
            patch(
                "src.models.tortoise.email_template.EmailTemplate.get_or_none",
                AsyncMock(return_value=mock_t),
            ),
            patch(
                "src.models.tortoise.email_template.EmailTemplateUsage.filter",
                return_value=mock_usage_qs,
            ),
        ):
            stats = await service.get_template_usage_stats(1, days=7)

        assert stats["total_usage"] == 2
        assert "usage_by_day" in stats

    async def test_get_template_usage_stats_not_found_raises(self):
        service = await self.async_set_up_service()
        with patch(
            "src.models.tortoise.email_template.EmailTemplate.get_or_none",
            AsyncMock(return_value=None),
        ):
            with pytest.raises(NotFoundError):
                await service.get_template_usage_stats(999)


# -------------------------
# private helpers
# -------------------------
def test_validate_template_syntax_raises():
    service = EmailTemplateService()
    with patch.object(
        service.jinja_env, "from_string", side_effect=TemplateError("bad")
    ):
        with pytest.raises(ValidationError):
            service._validate_template_syntax("{{ bad }}")


def test_render_template_success():
    service = EmailTemplateService()
    result = service._render_template("Hi {{ name }}", {"name": "Alice"})
    assert result == "Hi Alice"
