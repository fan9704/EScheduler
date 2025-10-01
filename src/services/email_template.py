import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from jinja2 import Template, Environment, BaseLoader, TemplateError
import re

from src.models.tortoise.email_template import EmailTemplate, EmailTemplateUsage
from src.models.pydantic.email_template import (
    EmailTemplateCreate, EmailTemplateUpdate, EmailTemplateResponse,
    EmailTemplatePreview, EmailTemplatePreviewResponse
)
from src.exceptions.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)


class EmailTemplateService:
    """Email 模板服務"""
    
    def __init__(self):
        self.jinja_env = Environment(loader=BaseLoader())
    
    async def create_template(self, template_data: EmailTemplateCreate) -> EmailTemplateResponse:
        """創建新的 Email 模板"""
        # 檢查名稱是否已存在
        existing = await EmailTemplate.filter(name=template_data.name).first()
        if existing:
            raise ValidationError(f"模板名稱 '{template_data.name}' 已存在")
        
        # 創建模板
        template = await EmailTemplate.create(
            name=template_data.name,
            description=template_data.description,
            subject_template=template_data.subject_template,
            body_template=template_data.body_template,
            html_template=template_data.html_template,
            variables=[var.dict() for var in template_data.variables],
            default_sender=template_data.default_sender,
            default_cc=template_data.default_cc,
            default_bcc=template_data.default_bcc,
            is_active=template_data.is_active
        )
        
        return EmailTemplateResponse.from_orm(template)

    async def list_templates(self, 
                           is_active: Optional[bool] = None,
                           search: Optional[str] = None,
                           limit: int = 100,
                           offset: int = 0) -> List[EmailTemplateResponse]:
        """獲取模板列表"""
        query = EmailTemplate.all()
        
        if is_active is not None:
            query = query.filter(is_active=is_active)
        
        if search:
            query = query.filter(name__icontains=search)
        
        templates = await query.order_by('-created_at').limit(limit).offset(offset)
        return [EmailTemplateResponse.from_orm(template) for template in templates]
    
    async def get_template(self, template_id: int) -> Optional[EmailTemplateResponse]:
        """獲取單個模板"""
        template = await EmailTemplate.get_or_none(id=template_id)
        if template:
            return EmailTemplateResponse.from_orm(template)
        return None
    
    async def update_template(self, template_id: int, 
                            template_data: EmailTemplateUpdate) -> Optional[EmailTemplateResponse]:
        """更新模板"""
        template = await EmailTemplate.get_or_none(id=template_id)
        if not template:
            raise NotFoundError(f"模板 ID {template_id} 不存在")
        
        # 檢查名稱衝突
        if template_data.name and template_data.name != template.name:
            existing = await EmailTemplate.get_or_none(name=template_data.name)
            if existing:
                raise ValidationError(f"模板名稱 '{template_data.name}' 已存在")
        
        # 更新字段
        update_data = template_data.dict(exclude_unset=True)
        if 'variables' in update_data:
            update_data['variables'] = [var.dict() for var in template_data.variables]
        
        await template.update_from_dict(update_data)
        await template.save()
        
        return EmailTemplateResponse.from_orm(template)

    async def delete_template(self, template_id: int) -> bool:
        """刪除模板"""
        template = await EmailTemplate.get_or_none(id=template_id)
        if not template:
            raise NotFoundError(f"模板 ID {template_id} 不存在")
        
        await template.delete()
        return True

    async def preview_template(self, preview_data: EmailTemplatePreview) -> EmailTemplatePreviewResponse:
        """預覽模板"""
        try:
            if preview_data.subject_template and (preview_data.body_template or preview_data.html_template):
                # 基於模板內容的預覽（優先）
                subject_template = preview_data.subject_template
                body_template = preview_data.body_template
                html_template = preview_data.html_template
            else:
                raise ValueError("必須提供 Subject 與 Body 或模板內容")
            
            # 驗證模板語法
            self._validate_template_syntax(subject_template)
            self._validate_template_syntax(body_template)
            if html_template:
                self._validate_template_syntax(html_template)
            
            # 渲染模板
            rendered_subject = self._render_template(
                subject_template, 
                preview_data.variables
            )
            rendered_body = ""
            if body_template:
                rendered_body = self._render_template(
                    body_template,
                    preview_data.variables
                )
            elif html_template:
                rendered_body = self._render_template(
                    html_template,
                    preview_data.variables
                )
            
            return EmailTemplatePreviewResponse(
                subject=rendered_subject,
                body=rendered_body,
                html_body="",
                variables_used=list(preview_data.variables.keys())
            )
            
        except TemplateError as e:
            raise ValidationError(f"模板語法錯誤: {str(e)}")
        except Exception as e:
            logger.error(f"預覽模板時發生錯誤: {str(e)}")
            raise ValidationError(f"預覽失敗: {str(e)}")

    async def get_template_usage_stats(self, template_id: int, 
                                     days: int = 30) -> Dict[str, Any]:
        """獲取模板使用統計"""
        template = await EmailTemplate.get_or_none(id=template_id)
        if not template:
            raise NotFoundError(f"模板 ID {template_id} 不存在")
        
        # 計算日期範圍
        end_date = datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        
        # 獲取使用記錄
        usage_records = await EmailTemplateUsage.filter(
            template_id=template_id,
            used_at__gte=start_date,
            used_at__lte=end_date
        ).all()
        
        return {
            "template_id": template_id,
            "template_name": template.name,
            "period_days": days,
            "total_usage": len(usage_records),
            "usage_by_day": [
                {
                    "date": record.used_at.date().isoformat(),
                    "count": 1
                }
                for record in usage_records
            ]
        }

    def _validate_template_syntax(self, template_str: str) -> None:
        """驗證模板語法"""
        try:
            self.jinja_env.from_string(template_str)
        except TemplateError as e:
            raise ValidationError(f"模板語法錯誤: {str(e)}")

    def _render_template(self, template_str: str, variables: Dict[str, Any]) -> str:
        """渲染模板"""
        template = self.jinja_env.from_string(template_str)
        return template.render(**variables)