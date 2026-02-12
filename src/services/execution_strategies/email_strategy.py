import asyncio
import re
import datetime as dt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, List, Optional

import aiosmtplib
from jinja2 import Environment, BaseLoader, TemplateError

from src.models.pydantic.strategy import ExecutionResult
from src.models.tortoise.email_template import EmailTemplate, EmailTemplateUsage
from src.configs.strategy_config import get_smtp_config
from . import ExecutionStrategy
from src.utils.logger import logger


class EmailExecutionStrategy(ExecutionStrategy):
    """Email 發送執行策略，支援模板功能"""

    def __init__(self):
        # 從統一配置系統載入 SMTP 配置
        smtp_config = get_smtp_config()

        self.smtp_host = smtp_config.host
        self.smtp_port = smtp_config.port
        self.smtp_username = smtp_config.username
        self.smtp_password = smtp_config.password
        self.use_tls = smtp_config.use_tls
        self.use_ssl = smtp_config.use_ssl
        self.default_from_email = smtp_config.default_from_email
        self.default_from_name = smtp_config.default_from_name

        self.jinja_env = Environment(loader=BaseLoader())

        logger.info(
            f"EmailExecutionStrategy 初始化完成 - SMTP: {self.smtp_host}:{self.smtp_port}, TLS: {self.use_tls}, SSL: {self.use_ssl}"
        )

    async def execute(
        self, target_arn: str, target_input: Dict[str, Any]
    ) -> ExecutionResult:
        """發送電子郵件（支援模板）"""
        start_time = asyncio.get_event_loop().time()

        try:
            if not self.validate_input(target_arn, target_input):
                return ExecutionResult(
                    success=False,
                    message="無效的 Email 參數",
                    data=None,  # 添加 data 字段
                    execution_time=0.0,
                )

            # 檢查是否使用模板
            use_template = target_input.get("use_template", False)
            template_id = target_input.get("template_id")

            if use_template and template_id:
                # 使用模板發送
                result = await self._send_with_template(
                    target_arn, target_input, start_time
                )
            else:
                # 直接發送
                result = await self._send_direct_email(
                    target_arn, target_input, start_time
                )

            return result

        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"Email 發送失敗: {e}")
            return ExecutionResult(
                success=False,
                message=f"Email 發送失敗: {str(e)}",
                data=None,
                execution_time=execution_time,
            )

    async def _send_with_template(
        self, target_arn: str, target_input: Dict[str, Any], start_time: float
    ) -> ExecutionResult:
        """使用模板發送郵件"""
        template_id = target_input.get("template_id")
        template_variables = target_input.get("template_variables", {})

        # 獲取模板
        template = await EmailTemplate.get_or_none(id=template_id, is_active=True)
        if not template:
            return ExecutionResult(
                success=False,
                message=f"找不到 ID 為 {template_id} 的活躍模板",
                data=None,
                execution_time=asyncio.get_event_loop().time() - start_time,
            )

        # 驗證模板變數
        validation_errors = template.validate_variables(template_variables)
        if validation_errors:
            return ExecutionResult(
                success=False,
                message=f"模板變數驗證失敗: {validation_errors}",
                data=None,
                execution_time=asyncio.get_event_loop().time() - start_time,
            )

        # 渲染模板
        try:
            rendered_subject = self._render_template(
                template.subject_template, template_variables
            )
            rendered_body = self._render_template(
                template.body_template, template_variables
            )
            rendered_html = None
            if template.html_template:
                rendered_html = self._render_template(
                    template.html_template, template_variables
                )
        except TemplateError as e:
            return ExecutionResult(
                success=False,
                message=f"模板渲染失敗: {str(e)}",
                data=None,
                execution_time=asyncio.get_event_loop().time() - start_time,
            )

        # 解析收件人資訊
        recipients = self._parse_recipients(target_arn, target_input)
        cc = target_input.get("cc", template.default_cc or [])
        bcc = target_input.get("bcc", template.default_bcc or [])
        sender = target_input.get(
            "sender",
            template.default_sender or self.smtp_username or "noreply@example.com",
        )

        # 發送郵件
        send_result = await self._send_email(
            recipients=recipients,
            cc=cc,
            bcc=bcc,
            sender=sender,
            subject=rendered_subject,
            body=rendered_body,
            html_body=rendered_html,
        )

        execution_time = asyncio.get_event_loop().time() - start_time

        # 記錄模板使用
        if send_result["success"]:
            usage_record = await self._create_usage_record(
                template=template,
                variables_used=template_variables,
                rendered_subject=rendered_subject,
                rendered_body=rendered_body,
                rendered_html=rendered_html,
                recipients=recipients,
                cc_recipients=cc,
                bcc_recipients=bcc,
                sender=sender,
                is_successful=True,
            )

            # 更新模板使用統計
            template.usage_count += 1
            template.last_used_at = dt.datetime.now()
            await template.save()

            return ExecutionResult(
                success=True,
                message="模板郵件發送成功",
                data={
                    "template_id": template_id,
                    "template_name": template.name,
                    "usage_record_id": usage_record.id,
                    "recipients": recipients,
                    "cc": cc,
                    "bcc": bcc,
                    "subject": rendered_subject,
                    "sender": sender,
                    "body_length": len(rendered_body),
                    "has_html": bool(rendered_html),
                },
                execution_time=execution_time,
            )
        else:
            # 記錄失敗的使用
            await self._create_usage_record(
                template=template,
                variables_used=template_variables,
                rendered_subject=rendered_subject,
                rendered_body=rendered_body,
                rendered_html=rendered_html,
                recipients=recipients,
                cc_recipients=cc,
                bcc_recipients=bcc,
                sender=sender,
                is_successful=False,
                error_message=send_result["error"],
            )

            return ExecutionResult(
                success=False,
                message=f"模板郵件發送失敗: {send_result['error']}",
                data=None,
                execution_time=execution_time,
            )

    async def _send_direct(
        self, target_arn: str, target_input: Dict[str, Any], start_time: float
    ) -> ExecutionResult:
        """直接發送郵件（不使用模板）"""
        recipients = self._parse_recipients(target_arn, target_input)
        subject = target_input.get("subject", "來自 EScheduler 的通知")
        body = target_input.get("body", "")
        html_body = target_input.get("html_body")
        sender = target_input.get("sender", self.smtp_username or "noreply@example.com")
        cc = target_input.get("cc", [])
        bcc = target_input.get("bcc", [])

        # 發送郵件
        send_result = await self._send_email(
            recipients=recipients,
            cc=cc,
            bcc=bcc,
            sender=sender,
            subject=subject,
            body=body,
            html_body=html_body,
        )

        execution_time = asyncio.get_event_loop().time() - start_time

        if send_result["success"]:
            return ExecutionResult(
                success=True,
                message="郵件發送成功",
                data={
                    "recipients": recipients,
                    "cc": cc,
                    "bcc": bcc,
                    "subject": subject,
                    "sender": sender,
                    "body_length": len(body) if body else 0,
                    "has_html": bool(html_body),
                },
                execution_time=execution_time,
            )
        else:
            return ExecutionResult(
                success=False,
                message=f"郵件發送失敗: {send_result['error']}",
                data=None,
                execution_time=execution_time,
            )

    async def _send_email(
        self,
        recipients: List[str],
        cc: List[str],
        bcc: List[str],
        sender: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> Dict[str, Any]:
        """發送郵件的核心方法"""
        try:
            # 創建郵件訊息
            message = MIMEMultipart("alternative")
            message["From"] = sender
            message["To"] = ", ".join(recipients)
            if cc:
                message["Cc"] = ", ".join(cc)
            message["Subject"] = subject

            # 添加文本內容
            if body:
                text_part = MIMEText(body, "html", "utf-8")
                message.attach(text_part)

            # 添加 HTML 內容
            if html_body:
                html_part = MIMEText(html_body, "html", "utf-8")
                message.attach(html_part)

            # 發送郵件 - 修復 Gmail SSL/TLS 配置
            all_recipients = recipients + cc + bcc

            # Gmail 特殊配置
            if "gmail.com" in self.smtp_host.lower():
                # Gmail 使用 STARTTLS，不是直接 SSL
                await aiosmtplib.send(
                    message,
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    username=self.smtp_username,
                    password=self.smtp_password,
                    start_tls=True,  # 使用 STARTTLS 而不是 use_tls
                    recipients=all_recipients,
                )
            else:
                # 其他 SMTP 服務器使用標準配置
                await aiosmtplib.send(
                    message,
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    username=self.smtp_username,
                    password=self.smtp_password,
                    use_tls=self.use_tls,
                    recipients=all_recipients,
                )

            logger.info(f"郵件發送成功: {len(all_recipients)} 個收件人")
            return {"success": True}

        except Exception as e:
            logger.error(f"SMTP 發送失敗: {str(e)}")
            return {"success": False, "error": str(e)}

    def _render_template(self, template_str: str, variables: Dict[str, Any]) -> str:
        """渲染 Jinja2 模板"""
        template = self.jinja_env.from_string(template_str)
        return template.render(**variables)

    async def _create_usage_record(
        self,
        template: EmailTemplate,
        variables_used: Dict[str, Any],
        rendered_subject: str,
        rendered_body: str,
        rendered_html: Optional[str],
        recipients: List[str],
        cc_recipients: List[str],
        bcc_recipients: List[str],
        sender: str,
        is_successful: bool,
        error_message: Optional[str] = None,
    ) -> EmailTemplateUsage:
        """創建模板使用記錄"""
        usage_record = await EmailTemplateUsage.create(
            template=template,
            variables_used=variables_used,
            rendered_subject=rendered_subject,
            rendered_body=rendered_body,
            rendered_html=rendered_html,
            recipients=recipients,
            cc_recipients=cc_recipients,
            bcc_recipients=bcc_recipients,
            sender=sender,
            is_successful=is_successful,
            error_message=error_message,
        )
        return usage_record

    def get_strategy_name(self) -> str:
        return "Email"

    def validate_input(self, target_arn: str, target_input: Dict[str, Any]) -> bool:
        """驗證 Email 參數"""
        if not target_arn:
            return False

        # 檢查是否使用模板
        use_template = target_input.get("use_template", False)

        if use_template:
            # 使用模板時必須提供 template_id
            if not target_input.get("template_id"):
                return False
        # 不使用模板時必須提供基本郵件內容
        elif not target_input.get("subject"):
            return False

        # 驗證郵件地址格式
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        recipients = self._parse_recipients(target_arn, target_input)
        for email in recipients:
            if not re.match(email_pattern, email):
                return False

        # 驗證 CC 和 BCC
        for field in ["cc", "bcc"]:
            emails = target_input.get(field, [])
            if emails:
                for email in emails:
                    if not re.match(email_pattern, email):
                        return False

        return True

    def _parse_recipients(
        self, target_arn: str, target_input: Dict[str, Any]
    ) -> List[str]:
        """解析收件人列表"""
        recipients = target_input.get("recipients", [])
        if not recipients:
            recipients = [target_arn]
        elif isinstance(recipients, str):
            recipients = [recipients]

        return recipients

    async def _send_direct_email(self, target_arn, target_input, start_time):
        recipients = self._parse_recipients(target_arn, target_input)
        subject = target_input.get("subject", "來自 EScheduler 的通知")
        body = target_input.get("body", "")
        html_body = target_input.get("html_body")
        sender = target_input.get("sender", self.smtp_username or "noreply@example.com")
        cc = target_input.get("cc", [])
        bcc = target_input.get("bcc", [])

        send_result = await self._send_email(
            recipients=recipients,
            cc=cc,
            bcc=bcc,
            sender=sender,
            subject=subject,
            body=body,
            html_body=html_body,
        )

        execution_time = asyncio.get_event_loop().time() - start_time

        if send_result["success"]:
            return ExecutionResult(
                success=True,
                message="郵件發送成功",
                data={
                    "recipients": recipients,
                    "cc": cc,
                    "bcc": bcc,
                    "subject": subject,
                    "sender": sender,
                    "body_length": len(body) if body else 0,
                    "has_html": bool(html_body),
                },
                execution_time=execution_time,
            )
        else:
            return ExecutionResult(
                success=False,
                message=f"郵件發送失敗: {send_result['error']}",
                data={
                    "recipients": recipients,
                    "cc": cc,
                    "bcc": bcc,
                    "subject": subject,
                    "sender": sender,
                    "body_length": len(body) if body else 0,
                    "has_html": bool(html_body),
                },
                execution_time=execution_time,
            )
