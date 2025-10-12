import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException
from datetime import datetime, timezone

from src.routers import email_template
from src.models.pydantic.email_template import (
    EmailTemplateCreate,
    EmailTemplateUpdate,
    EmailTemplatePreview,
)


# ---------------------------------------------------------------------------
# ✅ 建立 Email Template 測試
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_email_template_success():
    """測試成功建立 Email Template"""
    mock_service = AsyncMock()
    mock_service.create_template.return_value = {
        "id": 1,
        "name": "Welcome Template",
        "description": "歡迎信",
        "subject_template": "Welcome!",
        "body_template": "Hi {{name}}",
        "html_template": "<p>Hi {{name}}</p>",
        "variables": [{"name": "name", "type": "string"}],
        "default_sender": "noreply@example.com",
        "is_active": True,
        "is_system_template": False,
        "usage_count": 0,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    payload = EmailTemplateCreate(
        name="Welcome Template",
        subject_template="Welcome!",
        body_template="Hi {{name}}",
        html_template="<p>Hi {{name}}</p>",
        variables=[],
        default_sender="noreply@example.com",
        is_active=True,
    )

    result = await email_template.create_email_template(payload, service=mock_service)

    assert result["name"] == "Welcome Template"
    mock_service.create_template.assert_awaited_once_with(payload)


@pytest.mark.asyncio
async def test_create_email_template_exception():
    """測試建立 Email Template 發生例外"""
    mock_service = AsyncMock()
    mock_service.create_template.side_effect = Exception("DB Error")

    payload = EmailTemplateCreate(
        name="Fail Template",
        subject_template="Oops",
        body_template="Body",
    )

    with pytest.raises(HTTPException) as exc_info:
        await email_template.create_email_template(payload, service=mock_service)

    assert exc_info.value.status_code == 400
    assert "DB Error" in exc_info.value.detail


# ---------------------------------------------------------------------------
# ✅ 取得 Template 測試
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_email_template_not_found():
    """測試找不到 Template"""
    mock_service = AsyncMock()
    mock_service.get_template.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await email_template.get_email_template(999, service=mock_service)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "模板不存在"


@pytest.mark.asyncio
async def test_get_email_template_success():
    """測試成功取得 Template"""
    mock_service = AsyncMock()
    mock_service.get_template.return_value = {"id": 1, "name": "Welcome"}

    result = await email_template.get_email_template(1, service=mock_service)
    assert result["name"] == "Welcome"
    mock_service.get_template.assert_awaited_once_with(1)


# ---------------------------------------------------------------------------
# ✅ 更新 Template 測試
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_update_email_template_success():
    """測試成功更新 Template"""
    mock_service = AsyncMock()
    mock_service.update_template.return_value = {"id": 1, "name": "Updated"}

    payload = EmailTemplateUpdate(name="Updated")

    result = await email_template.update_email_template(1, payload, service=mock_service)
    assert result["name"] == "Updated"
    mock_service.update_template.assert_awaited_once_with(1, payload)


@pytest.mark.asyncio
async def test_update_email_template_not_found():
    """測試更新不存在的 Template"""
    mock_service = AsyncMock()
    mock_service.update_template.return_value = None

    payload = EmailTemplateUpdate(name="Updated")

    with pytest.raises(HTTPException) as exc_info:
        await email_template.update_email_template(999, payload, service=mock_service)

    assert exc_info.value.status_code == 404
    assert "模板不存在" in exc_info.value.detail


# ---------------------------------------------------------------------------
# ✅ 刪除 Template 測試
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_email_template_exception():
    """測試刪除失敗"""
    mock_service = AsyncMock()
    mock_service.delete_template.side_effect = Exception("Delete failed")

    with pytest.raises(HTTPException) as exc_info:
        await email_template.delete_email_template(1, service=mock_service)

    assert exc_info.value.status_code == 500
    assert "刪除模板失敗" in exc_info.value.detail


# ---------------------------------------------------------------------------
# ✅ 預覽 Template 測試
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_preview_email_template_success():
    """測試預覽模板成功"""
    mock_service = AsyncMock()
    mock_service.preview_template.return_value = {
        "subject": "Welcome John",
        "body": "Hi John",
        "html_body": "<p>Hi John</p>",
        "variables_used": ["name"],
    }

    payload = EmailTemplatePreview(
        subject_template="Welcome {{name}}",
        body_template="Hi {{name}}",
        html_template="<p>Hi {{name}}</p>",
        variables={"name": "John"},
    )

    result = await email_template.preview_email_template(payload, service=mock_service)

    assert result["subject"] == "Welcome John"
    mock_service.preview_template.assert_awaited_once_with(payload)


# ---------------------------------------------------------------------------
# ✅ 列表 Templates 測試
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_list_templates_success():
    mock_service = AsyncMock()
    mock_service.list_templates.return_value = [
        {"id": 1, "name": "Template 1"},
        {"id": 2, "name": "Template 2"},
    ]

    result = await email_template.list_templates(
        is_active=True,
        search="Welcome",
        limit=10,
        offset=0,
        service=mock_service
    )

    assert len(result) == 2
    mock_service.list_templates.assert_awaited_once_with(
        is_active=True, search="Welcome", limit=10, offset=0
    )


@pytest.mark.asyncio
async def test_list_templates_exception():
    mock_service = AsyncMock()
    mock_service.list_templates.side_effect = Exception("DB Error")

    with pytest.raises(Exception) as exc_info:
        await email_template.list_templates(
            service=mock_service
        )
    # 可以加 logger 檢查或直接 assert Exception message
    assert "DB Error" in str(exc_info.value)


# ---------------------------------------------------------------------------
# ✅ 刪除 Template 成功測試
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_delete_email_template_success():
    mock_service = AsyncMock()
    mock_service.delete_template.return_value = None  # delete 沒有回傳，router 成功會 204

    response = await email_template.delete_email_template(1, service=mock_service)

    # delete_email_template router 沒有返回值，FastAPI 會自動返回 204
    assert response is None
    mock_service.delete_template.assert_awaited_once_with(1)


# -----------------------------------------
# GET /{template_id} 發生 Exception
# -----------------------------------------
@pytest.mark.asyncio
async def test_get_email_template_exception():
    mock_service = AsyncMock()
    mock_service.get_template.side_effect = Exception("DB fail")

    with pytest.raises(HTTPException) as exc_info:
        await email_template.get_email_template(1, service=mock_service)

    assert exc_info.value.status_code == 500
    assert "獲取模板失敗" in exc_info.value.detail


# -----------------------------------------
# PUT /{template_id} 發生 Exception
# -----------------------------------------
@pytest.mark.asyncio
async def test_update_email_template_exception():
    mock_service = AsyncMock()
    mock_service.update_template.side_effect = Exception("Update fail")

    payload = EmailTemplateUpdate(name="Updated")

    with pytest.raises(HTTPException) as exc_info:
        await email_template.update_email_template(1, payload, service=mock_service)

    assert exc_info.value.status_code == 500
    assert "更新模板失敗" in exc_info.value.detail


# -----------------------------------------
# DELETE /{template_id} 發生 Exception
# -----------------------------------------
@pytest.mark.asyncio
async def test_delete_email_template_exception_router():
    mock_service = AsyncMock()
    mock_service.delete_template.side_effect = Exception("Delete fail")

    with pytest.raises(HTTPException) as exc_info:
        await email_template.delete_email_template(1, service=mock_service)

    assert exc_info.value.status_code == 500
    assert "刪除模板失敗" in exc_info.value.detail


# -----------------------------------------
# DELETE /{template_id} 發生 Exception
# -----------------------------------------
@pytest.mark.asyncio
async def test_delete_email_template_exception_router():
    mock_service = AsyncMock()
    mock_service.delete_template.side_effect = HTTPException(500, "Delete fail")

    with pytest.raises(HTTPException) as exc_info:
        await email_template.delete_email_template(1, service=mock_service)

    assert exc_info.value.status_code == 500
    assert "刪除模板失敗" in exc_info.value.detail


# -----------------------------------------
# POST /preview 發生 Exception
# -----------------------------------------
@pytest.mark.asyncio
async def test_preview_email_template_exception():
    mock_service = AsyncMock()
    mock_service.preview_template.side_effect = Exception("Preview fail")

    payload = EmailTemplatePreview(
        subject_template="Hi {{name}}",
        body_template="Body {{name}}",
        html_template="<p>{{name}}</p>",
        variables={"name": "John"},
    )

    with pytest.raises(HTTPException) as exc_info:
        await email_template.preview_email_template(payload, service=mock_service)

    assert exc_info.value.status_code == 400
    assert "Preview fail" in exc_info.value.detail
