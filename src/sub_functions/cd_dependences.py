import argparse
import logging
import os
from pathlib import Path

# Здесь собраны функции, необходимые основной функции - cd, чтобы не загрязнять и так грязный main


def cd_args_parse(args: list[str]) -> Path:
    """Проверяет аргумент path функции cd. Возвращает этот путь класса Path или ошибку."""
    parser = argparse.ArgumentParser(prog="cd", description="Смена текущей директории.", exit_on_error=False)
    parser.add_argument("path", help="Путь для смены каталога.")
    try:
        parsed_args = parser.parse_args(args)
        path_str = parsed_args.path
        if path_str == "~":
            path_str = os.path.expanduser("~")

        return Path(path_str)

    except argparse.ArgumentError as e:
        # Перехватываем ошибки парсинга
        raise Exception(f"Ошибка парсинга команды cd: {e}")

def cd_realisation(path: str) -> None:
    """Функция для смены директории для аргумента path. Тут всё очевидно."""
    try:
        if path == "~":
            path = os.path.expanduser("~")

        abs_path = os.path.abspath(path)
        os.chdir(abs_path)

    except PermissionError as e:
        logging.error(e)
        raise e
    except Exception as e:
        logging.error(e)
        raise e
