import logging
import sys
from typing import Any

# Здесь собраны функции, необходимые функции логирования, чтобы не загрязнять и так грязный main


# Конфигурация логирования
def setup_logging() -> None:
    """Настройка системы логирования."""
    logging.basicConfig(
        filename='/Users/kostamak/PycharmProjects/lab-2-cmd/src/sub_functions/shell.log',
        level=logging.INFO,
        format='[%(asctime)s] - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        encoding='utf-8'
    )


# Инициализация логирования
setup_logging()
logger = logging.getLogger(__name__)


def unhandled_exception(exc_type: Any, exc_value: Any, exc_traceback: Any) -> None:
    """Обработчик необработанных исключений."""
    if issubclass(exc_type, KeyboardInterrupt):
        # Пропускаем KeyboardInterrupt
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return


def logging_command(command: str, args: list[str]) -> None:
    """Логирует информацию о вызове команды."""
    full_command = f"{command} {' '.join(args)}".strip()
    logger.info(f"Выполнена команда: {full_command}")
