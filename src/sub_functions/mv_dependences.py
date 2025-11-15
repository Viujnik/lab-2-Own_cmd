import argparse
import os
import logging
from pathlib import Path


# Здесь собраны функции, необходимые основной функции - mv, чтобы не загрязнять и так грязный main

def mv_args_parse(args: list[str]) -> list[str]:
    """Парсит аргументы команды mv"""
    parser = argparse.ArgumentParser(
        prog="mv",
        description="Перемещает файл из path_from в path_to",
        exit_on_error=False
    )
    parser.add_argument("path_from", help="Путь откуда переместить")
    parser.add_argument("path_to", help="Путь куда переместить")

    try:
        parsed_args = parser.parse_args(args)
        return [parsed_args.path_from, parsed_args.path_to]
    except SystemExit:
        raise Exception("Ошибка парсинга команды mv: требуется 2 аргумента - путь_откуда и путь_куда")


def filesystem_check(path_from: str, path_to: str) -> bool:
    """Проверяет, в одной ли директории находятся файл и каталог назначения"""
    try:
        new_path_from = Path(path_from)
        new_path_to = Path(path_to)
        stat1 = os.stat(new_path_from)
        stat2 = os.stat(new_path_to)

        return stat1.st_dev == stat2.st_dev
    except OSError as e:
        error = f"Ошибка при проверке файловой системы: {e}"
        logging.error(error)
        return False
