"""
日志中间件
SCALE OS v10.0
"""

import time
import logging
from typing import Callable
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings


# 日志格式
class RequestFormatter(logging.Formatter):
    """请求日志格式化器"""

    def format(self, record):
        record.scale_version = settings.SCALE_VERSION
        return super().format(record)


# 配置日志
def setup_logging():
    """配置日志"""
    log_format = (
        "[%(asctime)s] [%(levelname)s] [%(name)s] "
        "[%(scale_version)s] %(message)s"
    )

    formatter = RequestFormatter(log_format)

    # 根日志
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    # 清除已有处理器
    root_logger.handlers.clear()

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    return root_logger


# 获取日志器
logger = logging.getLogger("scale")


class LoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成请求 ID
        request_id = str(uuid4())[:8]
        request.state.request_id = request_id

        # 记录请求开始
        start_time = time.time()
        method = request.method
        url = str(request.url)
        client_ip = request.client.host if request.client else "unknown"

        logger.info(f"[{request_id}] → {method} {url} | IP: {client_ip}")

        try:
            # 执行请求
            response = await call_next(request)

            # 计算耗时
            duration = (time.time() - start_time) * 1000
            status_code = response.status_code

            # 记录响应
            log_level = logging.INFO if status_code < 400 else logging.WARNING
            logger.log(
                log_level,
                f"[{request_id}] ← {status_code} | {duration:.2f}ms"
            )

            # 添加请求 ID 到响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration:.2f}ms"

            return response

        except Exception as e:
            # 记录异常
            duration = (time.time() - start_time) * 1000
            logger.error(
                f"[{request_id}] ✗ {type(e).__name__}: {str(e)} | {duration:.2f}ms"
            )
            raise


class ContextFilter(logging.Filter):
    """上下文过滤器"""

    def filter(self, record):
        record.scale_version = getattr(settings, "SCALE_VERSION", "10.0")
        return True


# 应用日志配置
setup_logging()
