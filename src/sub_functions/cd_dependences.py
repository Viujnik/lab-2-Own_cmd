import logging
import os
from pathlib import Path


# Здесь собраны функции, необходимые основной функции - cd, чтобы не загрязнять и так грязный main


def cd_args_parse(args: list[str]) -> None | Path:
    """Проверяет аргумент path функции cd. Возвращает этот путь класса Path или None при ошибке."""
    if args[0]:
        arg = Path(args[0])
        if arg.exists():  # Проверка существования пути
            return arg
        return None
    else:
        error = "Для команды cd ожидается 2-ой аргумент - path"
        print(error)
        logging.error(error)
        return None


def cd_realisation(path: str) -> None:
    """Функция для смены директории для аргумента path. Тут всё очевидно."""
    if path == "~":
        os.chdir(os.path.expanduser("~"))
    else:
        os.chdir(path)
