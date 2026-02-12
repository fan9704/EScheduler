import aiohttp
import asyncio
from typing import Dict, Any
from . import ExecutionStrategy
from src.models.pydantic.strategy import ExecutionResult, HTTPResult
from src.configs.strategy_config import get_http_config
from src.utils.logger import logger
from src.consts import HTTP_OK, HTTP_MULTIPLE_CHOICES


class HttpExecutionStrategy(ExecutionStrategy):
    """HTTP 請求執行策略"""

    def __init__(self):
        # 從統一配置系統載入 HTTP 配置
        http_config = get_http_config()

        self.timeout = aiohttp.ClientTimeout(total=http_config.timeout)
        self.max_retries = http_config.max_retries
        self.verify_ssl = http_config.verify_ssl

        logger.info(
            f"HttpExecutionStrategy 初始化完成 - timeout: {http_config.timeout}s, max_retries: {http_config.max_retries}"
        )

    async def execute(
        self, target_arn: str, target_input: Dict[str, Any]
    ) -> ExecutionResult:
        """執行 HTTP 請求"""
        start_time = asyncio.get_event_loop().time()

        try:
            if not self.validate_input(target_arn, target_input):
                return ExecutionResult(
                    success=False, message="無效的 HTTP 請求參數", execution_time=0.0
                )

            method = target_input.get("method", "GET").upper()
            headers = target_input.get("headers", {})
            data = target_input.get("data", {})
            params = target_input.get("params", {})

            # 設置預設 headers
            default_headers = {
                "User-Agent": "EScheduler/1.0",
                "Accept": "application/json",
            }
            default_headers.update(headers)

            logger.info(f"執行 HTTP {method} 請求: {target_arn}")
            logger.info(f"請求參數: {params}")
            logger.info(f"請求頭: {default_headers}")

            # 使用配置的 SSL 驗證設置
            connector = aiohttp.TCPConnector(ssl=self.verify_ssl)

            async with aiohttp.ClientSession(
                timeout=self.timeout, connector=connector
            ) as session:
                try:
                    response = await session.request(
                        method=method,
                        url=target_arn,
                        headers=default_headers,
                        json=data
                        if data and method in ["POST", "PUT", "PATCH"]
                        else None,
                        params=params,
                    )
                    response_text = await response.text()
                    execution_time = asyncio.get_event_loop().time() - start_time

                    logger.info(f"HTTP 回應狀態: {response.status}")
                    logger.info(
                        f"HTTP 回應內容: {response_text[:200]}..."
                    )  # 只記錄前200字符

                    success = HTTP_OK <= response.status < HTTP_MULTIPLE_CHOICES
                    http_result = HTTPResult(
                        method=method,
                        url=str(response.url),
                        request_headers=default_headers,
                        request_params=params,
                        request_data=data,
                        response_body=response_text,
                        response_headers=dict(response.headers),
                    )

                    return ExecutionResult(
                        success=success,
                        message=f"HTTP {method} 請求{'成功' if success else '失敗'} (狀態碼: {response.status})",
                        data=http_result,
                        execution_time=execution_time,
                        status_code=response.status,
                    )

                except aiohttp.ClientConnectorError as e:
                    execution_time = asyncio.get_event_loop().time() - start_time
                    logger.error(f"連接錯誤: {str(e)}")
                    return ExecutionResult(
                        success=False,
                        message=f"連接失敗: {str(e)}",
                        execution_time=execution_time,
                    )
                except aiohttp.ClientResponseError as e:
                    execution_time = asyncio.get_event_loop().time() - start_time
                    logger.error(f"HTTP 回應錯誤: {str(e)}")
                    return ExecutionResult(
                        success=False,
                        message=f"HTTP 回應錯誤: {str(e)}",
                        execution_time=execution_time,
                    )
                except asyncio.TimeoutError:
                    execution_time = asyncio.get_event_loop().time() - start_time
                    logger.error(f"請求超時 (>{self.timeout.total}秒)")
                    return ExecutionResult(
                        success=False,
                        message=f"HTTP 請求超時 (>{self.timeout.total}秒)",
                        execution_time=execution_time,
                    )

        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"HTTP 請求異常: {str(e)}")
            return ExecutionResult(
                success=False,
                message=f"HTTP 請求異常: {str(e)}",
                data=None,
                execution_time=execution_time,
            )

    def get_strategy_name(self) -> str:
        return "HTTP"

    def validate_input(self, target_arn: str, target_input: Dict[str, Any]) -> bool:
        """驗證 HTTP 請求參數"""
        if not target_arn:
            logger.error("target_arn 不能為空")
            return False

        if not target_arn.startswith(("http://", "https://")):
            logger.error(f"無效的 URL 格式: {target_arn}")
            return False

        method = target_input.get("method", "GET").upper()
        if method not in ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]:
            logger.error(f"不支援的 HTTP 方法: {method}")
            return False

        return True
