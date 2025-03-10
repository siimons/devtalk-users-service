from fastapi import Request, status
from fastapi.responses import JSONResponse

from slowapi.errors import RateLimitExceeded


class RateLimitExceededError(RateLimitExceeded):
    """
    Пользовательское исключение для обработки превышения лимита запросов.

    Args:
        retry_after (int): Время в секундах, через которое можно повторить запрос.
        detail (str, optional): Детальное сообщение об ошибке. По умолчанию "Too many requests".
    """

    def __init__(self, retry_after: int, detail: str = "Too many requests"):
        super().__init__(detail)
        self.retry_after = retry_after


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Обработчик ошибок для Rate Limiting.

    Args:
        request (Request): Запрос, вызвавший ошибку.
        exc (RateLimitExceeded): Исключение RateLimitExceeded или RateLimitExceededError.

    Returns:
        JSONResponse: Ответ с кодом 429 и деталями ошибки.
    """
    headers = {}
    if isinstance(exc, RateLimitExceededError):
        headers["Retry-After"] = str(exc.retry_after)
    elif hasattr(exc, "retry_after"):
        headers["Retry-After"] = str(exc.retry_after)

    detail_message = exc.detail if hasattr(exc, "detail") else "Too many requests. Please try again later."
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": detail_message},
        headers=headers,
    )