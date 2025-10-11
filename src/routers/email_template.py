from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from src.models.pydantic.email_template import (
    EmailTemplateCreate,
    EmailTemplateUpdate,
    EmailTemplateResponse,
    EmailTemplatePreview,
    EmailTemplatePreviewResponse
)
from src.services.email_template import EmailTemplateService
from src.dependencies.services import get_email_template_service
from src.utils.logger import logger

router = APIRouter()


@router.get("", response_model=List[EmailTemplateResponse])
async def list_templates(
        is_active: Optional[bool] = Query(None, description="是否啟用"),
        search: Optional[str] = Query(None, description="搜索關鍵字"),
        limit: int = Query(100, ge=1, le=1000, description="返回數量限制"),
        offset: int = Query(0, ge=0, description="偏移量"),
        service: EmailTemplateService = Depends(get_email_template_service)
):
    """獲取 Email 模板列表"""
    return await service.list_templates(
        is_active=is_active,
        search=search,
        limit=limit,
        offset=offset
    )


@router.post("", response_model=EmailTemplateResponse)
async def create_email_template(
        template_data: EmailTemplateCreate,
        service: EmailTemplateService = Depends(get_email_template_service)
):
    """創建新的 Email 模板"""
    try:
        return await service.create_template(template_data)
    except Exception as e:
        logger.error(f"創建模板失敗: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{template_id}", response_model=EmailTemplateResponse)
async def get_email_template(
        template_id: int,
        service: EmailTemplateService = Depends(get_email_template_service)
):
    """獲取單個 Email 模板"""
    try:
        template = await service.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="模板不存在")
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取模板失敗: {str(e)}")
        raise HTTPException(status_code=500, detail="獲取模板失敗")


@router.put("/{template_id}", response_model=EmailTemplateResponse)
async def update_email_template(
        template_id: int,
        template_data: EmailTemplateUpdate,
        service: EmailTemplateService = Depends(get_email_template_service)
):
    """更新 Email 模板"""
    try:
        template = await service.update_template(template_id, template_data)
        if not template:
            raise HTTPException(status_code=404, detail="模板不存在")
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新模板失敗: {str(e)}")
        raise HTTPException(status_code=500, detail="更新模板失敗")


@router.delete("/{template_id}", status_code=204)
async def delete_email_template(
        template_id: int,
        service: EmailTemplateService = Depends(get_email_template_service)
):
    """刪除 Email 模板"""
    try:
        await service.delete_template(template_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刪除模板失敗: {str(e)}")
        raise HTTPException(status_code=500, detail="刪除模板失敗")


@router.post("/preview", response_model=EmailTemplatePreviewResponse)
async def preview_email_template(
        preview_data: EmailTemplatePreview,
        service: EmailTemplateService = Depends(get_email_template_service)
):
    """預覽 Email 模板"""
    try:
        return await service.preview_template(preview_data)
    except Exception as e:
        logger.error(f"預覽模板失敗: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
