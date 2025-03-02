from fastapi import Request, status
from fastapi.responses import JSONResponse

from slowapi.errors import RateLimitExceeded


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Обработчик ошибок для Rate Limiting.

    Args:
        request (Request): Запрос, вызвавший ошибку.
        exc (RateLimitExceeded): Исключение RateLimitExceeded.

    Returns:
        JSONResponse: Ответ с кодом 429 и деталями ошибки.
    """
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Too many requests. Please try again later."},
        headers={"Retry-After": str(exc.retry_after)},
    )