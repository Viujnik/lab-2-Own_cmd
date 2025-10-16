import logging
import shutil
from pathlib import Path


# Здесь собраны функции, необходимые основной функции - cat, чтобы не загрязнять и так грязный main


def cp_args_parse(args: list) -> list:
    if len(args) == 2:
        path_from = Path(args[0])
        path_to = Path(args[1])
        if not path_from.exists():
            error = f"Файл {path_from} не найден."
            logging.error(error)
            raise FileNotFoundError(error)
        if not path_to.exists():
            error = f"Директория {path_from} не найдена."
            logging.error(error)
            raise NotADirectoryError(error)
        return [path_from, path_to]
    else:
        error = "Введите 2 аргумента: файл и дерикторию."
        logging.error(error)
        raise Exception(error)


def cp_realisation(arg_value: list) -> None:
    try:
        shutil.copy(arg_value[0], arg_value[1])
    except PermissionError:
        error = "Ошибка: недостаточно прав для копирования файла"
        logging.error(error)
        raise PermissionError(error)
