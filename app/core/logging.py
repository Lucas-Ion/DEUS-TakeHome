"""
logging.py configures logging using Loguru.

There are two logging sinks:
  1. stdout  - always active, structured for local development
  2. Azure Application Insights - active only when connection string is set

Usage:
    from app.core.logging import setup_logging

    setup_logging()
"""

import logging
import sys

from loguru import logger

from app.core.config import get_settings


class InterceptHandler(logging.Handler):
    """
    Intercepts standard library logging and routes through Loguru.

    This ensures that logs from SQLAlchemy, uvicorn, and FastAPI all flow
    through a single Loguru pipeline rather than going around it.
    """

    def emit(self, record: logging.LogRecord) -> None:
        """
        Intercept a standard logging record and I re-emit via Loguru.
        """
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore[assignment]
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging() -> None:
    """
    Initialise Loguru with stdout and App Insights sinks.
    """
    settings = get_settings()

    logger.remove()

    logger.add(
        sys.stdout,
        level=settings.log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        colorize=True,
        backtrace=True,
        diagnose=settings.debug,
    )

    loggers_to_intercept = [
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "fastapi",
        "sqlalchemy.engine",
    ]
    for name in loggers_to_intercept:
        std_logger = logging.getLogger(name)
        std_logger.handlers = [InterceptHandler()]
        std_logger.propagate = False

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    if settings.app_insights_enabled:
        _setup_app_insights(settings.applicationinsights_connection_string)  # type: ignore[arg-type]

    logger.info(
        "Logging initialised | environment={} | level={} | app_insights={}",
        settings.environment,
        settings.log_level,
        settings.app_insights_enabled,
    )


def _setup_app_insights(connection_string: str) -> None:
    """
    Azure Monitor OpenTelemetry exporter.

    Traces, logs, and exceptions are forwarded to Application Insights.
    """
    try:
        from azure.monitor.opentelemetry import configure_azure_monitor

        configure_azure_monitor(connection_string=connection_string)
        logger.info("Azure Application Insights sink configured.")
    except ImportError:
        logger.warning(
            "azure-monitor-opentelemetry is not installed. App Insights sink will not be active."
        )
    except Exception as exc:
        logger.error("Failed to configure App Insights: {}", exc)
