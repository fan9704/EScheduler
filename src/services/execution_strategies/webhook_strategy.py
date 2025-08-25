import aiohttp
import asyncio
import logging
import json
from typing import Dict, Any
from . import ExecutionStrategy, ExecutionResult

logger = logging.getLogger(__name__)


class WebhookExecutionStrategy(ExecutionStrategy):
    """Webhook 執行策略"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
    
    async def execute(self, target_arn: str, target_input: Dict[str, Any]) -> ExecutionResult:
        """執行 Webhook 調用"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            if not self.validate_input(target_arn, target_input):
                return ExecutionResult(
                    success=False,
                    message="無效的 Webhook 參數",
                    execution_time=0.0
                )
            
            # Webhook 通常使用 POST 方法
            method = target_input.get('method', 'POST').upper()
            headers = target_input.get('headers', {})
            body = target_input.get('body', {})

            # 設置 Webhook 專用 headers
            webhook_headers = {
                'User-Agent': 'EScheduler-Webhook/1.0',
                'Content-Type': 'application/json',
                'X-Webhook-Source': 'EScheduler'
            }
            
            # 添加簽名（如果提供了密鑰）
            if secret:
                import hmac
                import hashlib
                payload_str = json.dumps(body, sort_keys=True)
                signature = hmac.new(
                    secret.encode('utf-8'),
                    payload_str.encode('utf-8'),
                    hashlib.sha256
                ).hexdigest()
                webhook_headers['X-Webhook-Signature'] = f"sha256={signature}"
            
            webhook_headers.update(headers)
            
            logger.info(f"執行 Webhook 調用: {target_arn}")

            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.request(
                    method=method,
                    url=target_arn,
                    headers=webhook_headers,
                    json=payload
                ) as response:
                    response_text = await response.text()
                    execution_time = asyncio.get_event_loop().time() - start_time
                    
                    success = 200 <= response.status < 300
                    
                    return ExecutionResult(
                        success=success,
                        message=f"Webhook 調用{'成功' if success else '失敗'}",
                        data={
                            'method': method,
                            'url': str(response.url),
                            'payload': payload,
                            'has_signature': bool(secret),
                            'response_body': response_text,
                            'response_headers': dict(response.headers)
                        },
                        execution_time=execution_time,
                        status_code=response.status
                    )
                    
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            return ExecutionResult(
                success=False,
                message=f"Webhook 調用失敗: {str(e)}",
                execution_time=execution_time
            )
    
    def get_strategy_name(self) -> str:
        return "Webhook"
    
    def validate_input(self, target_arn: str, target_input: Dict[str, Any]) -> bool:
        """驗證 Webhook 參數"""
        if not target_arn or not target_arn.startswith(('http://', 'https://')):
            return False
        return True