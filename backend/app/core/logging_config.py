"""Базовая конфигурация логирования. Можно расширять под StructLog, JSON и т.д."""

import logging
import sys
from typing import Optional


def setup_logging(level: Optional[int] = logging.INFO) -> None:
    """Настраивает корневое логирование приложения."""
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Избегаем дублирования handlers при повторном вызове
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)

    # Уровни для модулей приложения (заготовка для расширения)
    for module in ["app.services", "app.crud", "app.routers", "app.seed_data"]:
        mod_logger = logging.getLogger(module)
        mod_logger.setLevel(level)