import time
from typing import Tuple

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from prometheus_client import (
    Histogram,
    Gauge,
    Counter,
    generate_latest,
    CONTENT_TYPE_LATEST,
    REGISTRY,
)

from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_fastapi_instrumentator.metrics import Info

from app.core.settings import settings

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total count of HTTP requests",
    ["method", "endpoint", "status_code"]
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"]
)

ACTIVE_REQUESTS = Gauge(
    "http_requests_in_progress",
    "Number of active HTTP requests",
    ["method", "endpoint"]
)

APPLICATION_INFO = Gauge(
    "application_info",
    "Application version information",
    ["version", "environment"]
)

EXCEPTION_COUNT = Counter(
    "http_exceptions_total",
    "Total count of HTTP exceptions",
    ["method", "endpoint", "exception_type"]
)


def latency_buckets() -> Tuple[float, ...]:
    """
    Определение бакетов для гистограмм latency.

    Returns:
        Tuple[float, ...]: Границы бакетов в секундах.
    """
    return (.005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0, 2.5, 5.0, 7.5, 10.0, 30.0, 60.0)


def http_requests_total() -> None:
    """Кастомная метрика для общего количества HTTP запросов."""
    def instrumentation(info: Info) -> None:
        REQUEST_COUNT.labels(
            method=info.request.method,
            endpoint=info.modified_handler,
            status_code=info.response.status_code
        ).inc()

    return instrumentation


def http_request_duration() -> None:
    """Кастомная метрика для длительности HTTP запросов."""
    def instrumentation(info: Info) -> None:
        if hasattr(info, "duration"):
            REQUEST_DURATION.labels(
                method=info.request.method,
                endpoint=info.modified_handler
            ).observe(info.duration)

    return instrumentation


def create_instrumentator() -> Instrumentator:
    """
    Создание и конфигурация Prometheus instrumentator.

    Returns:
        Instrumentator: Сконфигурированный экземпляр Prometheus instrumentator.
    """
    instrumentator = Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics", "/health", "/api/docs", "/api/redoc", "/api/openapi.json"],
        inprogress_name="http_requests_in_progress",
        inprogress_labels=True,
    )

    instrumentator.add(http_requests_total())
    instrumentator.add(http_request_duration())

    return instrumentator


def setup_application_metrics(app: FastAPI, version: str = "1.0.0", environment: str = "development") -> None:
    """
    Настройка метрик информации о приложении.

    Args:
        app: Экземпляр FastAPI приложения.
        version: Версия приложения.
        environment: Окружение развертывания.
    """
    APPLICATION_INFO.labels(version=settings.APP_VERSION, environment=settings.ENVIRONMENT).set(1)


class MonitoringMiddleware:
    """Middleware для комплексного мониторинга запросов."""

    def __init__(self, app: FastAPI):
        """
        Инициализация monitoring middleware.

        Args:
            app: Экземпляр FastAPI приложения.
        """
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        """
        Обработка запроса и сбор метрик.

        Args:
            scope: Scope запроса.
            receive: Receive channel.
            send: Send channel.
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        method = request.method
        endpoint = request.url.path

        # Отслеживание активных запросов
        ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).inc()

        start_time = time.time()

        try:
            await self.app(scope, receive, send)
        except Exception as e:
            EXCEPTION_COUNT.labels(
                method=method,
                endpoint=endpoint,
                exception_type=type(e).__name__
            ).inc()
            raise
        finally:
            duration = time.time() - start_time
            ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).dec()

            # Запись длительности для всех запросов
            REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)


def create_metrics_router(app: FastAPI) -> None:
    """
    Создание эндпоинтов для метрик.

    Args:
        app: Экземпляр FastAPI приложения.
    """
    @app.get("/metrics", include_in_schema=False)
    async def metrics_endpoint() -> Response:
        """
        Экспорт метрик Prometheus.

        Returns:
            Response: Метрики Prometheus в текстовом формате.
        """
        return Response(
            content=generate_latest(REGISTRY),
            media_type=CONTENT_TYPE_LATEST
        )

    @app.get("/health", include_in_schema=False)
    async def health_check() -> JSONResponse:
        """
        Health check эндпоинт для балансировщиков и мониторинга.

        Returns:
            JSONResponse: Ответ со статусом здоровья.
        """
        return JSONResponse(
            content={"status": "healthy", "timestamp": time.time()},
            status_code=200
        )


def setup_monitoring(app: FastAPI) -> None:
    """
    Настройка комплексного мониторинга для FastAPI приложения.

    Функция конфигурирует все компоненты мониторинга включая:
    - Сбор метрик Prometheus
    - Health checks
    - Middleware для мониторинга запросов

    Args:
        app: Экземпляр FastAPI приложения для инструментирования.
    """
    create_metrics_router(app)

    app.add_middleware(MonitoringMiddleware)

    instrumentator = create_instrumentator()
    instrumentator.instrument(app)
