"""
异常处理
SCALE OS v10.0
"""

from typing import Any, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pydantic import ValidationError

from app.utils.response import ApiResponse


class AppException(Exception):
    """应用异常基类"""

    def __init__(
        self,
        message: str,
        code: int = status.HTTP_400_BAD_REQUEST,
        data: Optional[Any] = None,
    ):
        self.message = message
        self.code = code
        self.data = data
        super().__init__(message)


class NotFoundException(AppException):
    """资源不存在异常"""

    def __init__(self, message: str = "资源不存在"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class UnauthorizedException(AppException):
    """未授权异常"""

    def __init__(self, message: str = "未授权访问"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(AppException):
    """禁止访问异常"""

    def __init__(self, message: str = "权限不足"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class BadRequestException(AppException):
    """错误请求异常"""

    def __init__(self, message: str = "请求参数错误"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class ConflictException(AppException):
    """冲突异常"""

    def __init__(self, message: str = "资源冲突"):
        super().__init__(message, status.HTTP_409_CONFLICT)


class InternalException(AppException):
    """内部错误异常"""

    def __init__(self, message: str = "服务器内部错误"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """应用异常处理器"""
    return JSONResponse(
        status_code=exc.code,
        content=ApiResponse.error(
            message=exc.message,
            code=exc.code,
            data=exc.data,
        ).model_dump(),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP 异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse.error(
            message=exc.detail,
            code=exc.status_code,
        ).model_dump(),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """验证异常处理器"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ApiResponse.error(
            message="参数验证失败",
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            data={"errors": errors},
        ).model_dump(),
    )


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """数据库完整性异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=ApiResponse.error(
            message="数据冲突，可能已存在相同记录",
            code=status.HTTP_409_CONFLICT,
        ).model_dump(),
    )


async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """数据库异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ApiResponse.error(
            message="数据库操作失败",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ).model_dump(),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """通用异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ApiResponse.error(
            message="服务器内部错误",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ).model_dump(),
    )
