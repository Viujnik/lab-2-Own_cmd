import os
import logging
from pathlib import Path


# Здесь собраны функции, необходимые основной функции - mv, чтобы не загрязнять и так грязный main

def mv_args_parse(args: list[str]) -> list[str]:
    if len(args) != 2:
        error = "Ошибка: После команды 'mv' введите 2 аргумента - путь к файлу и каталог, куда переместить файл."
        raise Exception(error)
    else:
        path_from, path_to = args
        if not os.path.isdir(path_to):
            error = f"Ошибка: {path_to} не является директорией, введите директория куда переместить файл."
            raise Exception(error)
        if not os.path.exists(path_from):
            error = f"Файла {path_from} не существует."
            raise Exception(error)
        if not os.path.exists(path_to):
            error = f"Директории {path_from} не существует."
            raise Exception(error)
        return [path_from, path_to]


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
