import aiosmtplib
import asyncio
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
from . import ExecutionStrategy, ExecutionResult

logger = logging.getLogger(__name__)


class EmailExecutionStrategy(ExecutionStrategy):
    """Email 發送執行策略"""
    
    def __init__(self, smtp_host: str = "localhost", smtp_port: int = 587, 
                 smtp_username: str = None, smtp_password: str = None,
                 use_tls: bool = True):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.use_tls = use_tls
    
    async def execute(self, target_arn: str, target_input: Dict[str, Any]) -> ExecutionResult:
        """發送電子郵件"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            if not self.validate_input(target_arn, target_input):
                return ExecutionResult(
                    success=False,
                    message="無效的 Email 參數",
                    execution_time=0.0
                )
            
            # 解析郵件參數
            recipients = self._parse_recipients(target_arn, target_input)
            subject = target_input.get('subject', '來自 EScheduler 的通知')
            body = target_input.get('body', '')
            html_body = target_input.get('html_body')
            sender = target_input.get('sender', self.smtp_username or 'noreply@example.com')
            cc = target_input.get('cc', [])
            bcc = target_input.get('bcc', [])
            
            logger.info(f"發送郵件到: {recipients}")
            
            # 創建郵件
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = sender
            message['To'] = ', '.join(recipients)
            
            if cc:
                message['Cc'] = ', '.join(cc)
            
            # 添加文本內容
            if body:
                text_part = MIMEText(body, 'plain', 'utf-8')
                message.attach(text_part)
            
            # 添加 HTML 內容
            if html_body:
                html_part = MIMEText(html_body, 'html', 'utf-8')
                message.attach(html_part)
            
            # 發送郵件
            all_recipients = recipients + cc + bcc
            
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                use_tls=self.use_tls,
                recipients=all_recipients
            )
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return ExecutionResult(
                success=True,
                message="郵件發送成功",
                data={
                    'recipients': recipients,
                    'cc': cc,
                    'bcc': bcc,
                    'subject': subject,
                    'sender': sender,
                    'body_length': len(body) if body else 0,
                    'has_html': bool(html_body)
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            return ExecutionResult(
                success=False,
                message=f"郵件發送失敗: {str(e)}",
                execution_time=execution_time
            )
    
    def get_strategy_name(self) -> str:
        return "Email"
    
    def validate_input(self, target_arn: str, target_input: Dict[str, Any]) -> bool:
        """驗證 Email 參數"""
        if not target_arn:
            return False
        
        # 簡單的郵件地址驗證
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        recipients = self._parse_recipients(target_arn, target_input)
        for email in recipients:
            if not re.match(email_pattern, email):
                return False
        
        return True
    
    def _parse_recipients(self, target_arn: str, target_input: Dict[str, Any]) -> List[str]:
        """解析收件人列表"""
        recipients = target_input.get('recipients', [])
        if not recipients:
            recipients = [target_arn]
        elif isinstance(recipients, str):
            recipients = [recipients]
        
        return recipients