import logging
import os
import shutil
from pathlib import Path


# Здесь собраны функции, необходимые основной функции - rm, чтобы не загрязнять и так грязный main

def windows_check(path_check: str) -> bool:
    path = os.path.normpath(path_check)
    drive, symb = os.path.splitdrive(path)
    return bool(drive) and symb in ('\\', '/', '')


def rm_args_parse(args: list[str]) -> dict[str, object]:
    """Парсит аргументы команды rm и смотрит, какие переданы, а какие нет"""
    parsed_args = {
        "r_flag": False,
        "path": ''
    }
    i = 0
    while i < len(args):
        cur_arg = args[i]
        if cur_arg.startswith("-"):
            if cur_arg == "-r":
                parsed_args["r_flag"] = True
        else:
            parsed_args["path"] = os.path.normpath(args[i])
        i += 1
    if not parsed_args["path"]:
        error_msg = "Пустой аргумент пути/файла для команды mv."
        raise Exception(error_msg)
    return parsed_args


def rm_realisation(args: dict[str, object]) -> None:
    """Реализация удаления файла или каталога"""
    path = str(args["path"])
    r_flag = args["r_flag"]
    if os.path.dirname(os.path.normpath(path)) == os.path.normpath(path):
        error_msg = "Ошибка: нельзя удалить родительский каталог."
        raise Exception(error_msg)
    elif path == "/" or windows_check(path):
        error_msg = "Ошибка: нельзя удалить корневой каталог."
        raise Exception(error_msg)

    user_confirmation = input(f"Вы уверены, что хотите удалить {path}?\n"
                              f"(y - для подтверждения, любой другой ввод для прерывая удаления): ")
    if user_confirmation == "y":
        path = path
        try:
            if Path.is_file(Path(path)):
                os.remove(path)
            elif Path.is_dir(Path(path)):
                if r_flag:
                    shutil.rmtree(path)
                else:
                    error_msg = f"Нельзя удалить {path}, так как это директория. Попробуйте ввести флаг <-r>."
                    raise Exception(error_msg)
        except PermissionError:
            error_msg = f"Недостаточно прав на удаление {path}."
            raise Exception(error_msg)
        except FileNotFoundError:
            error_msg = f"не удаётся найти {path}."
            raise FileNotFoundError(error_msg)
        except Exception as e:
            error_msg = f"Произошла ошибка при удалении: {e}."
            raise Exception(error_msg)
    else:
        message = "Удаление прервано."
        logging.info(message)
