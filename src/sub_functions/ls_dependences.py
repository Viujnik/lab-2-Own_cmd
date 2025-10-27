import logging
import os
from os import stat_result
from pathlib import Path
from datetime import datetime
import stat

# Здесь собраны функции, необходимые основной функции - ls, чтобы не загрязнять и так грязный main


def check_access_rights(file_stat: stat_result) -> str:
    """Возвращает права доступа для файла"""
    rights = stat.filemode(file_stat.st_mode)
    return str(rights)[-9:]


def detailed_list(files: list[Path]) -> None:
    """Детальный вывод для флага <-l>"""
    for file in files:
        try:
            file_stat = file.stat()

            # Получаем всю информацию из объекта stat
            rights = check_access_rights(file_stat)
            links_cnt = file_stat.st_nlink
            file_uid = file_stat.st_uid
            file_gid = file_stat.st_gid
            file_size = file_stat.st_size
            mtime = datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')

            # Определяем имя с учетом символических ссылок
            display_name = file.name
            if stat.S_ISLNK(file_stat.st_mode):
                try:
                    linked_file = os.readlink(file)
                    display_name = f"{file.name} -> {linked_file}"
                except OSError:
                    display_name = f"{file.name} -> [broken link]"

            # Вывод всей информации форматированием
            print(f"{rights} {links_cnt:>2} {file_uid} {file_gid} {file_size:>10} {mtime} {display_name}")

        except OSError as e:
            raise e
        except Exception as e:
            raise e


def ls_realisation(path: str, long: bool = False) -> None:
    """Основная логика команды ls с улучшенной обработкой ошибок"""
    try:
        # Определяем целевой путь
        if path:
            list_path = Path(path)
        else:
            list_path = Path.cwd()

        # Проверяем существование пути
        if not list_path.exists():
            error_msg = f"Нет такого файла/директории, {list_path}"
            raise Exception(error_msg)

        # Проверяем, что это директория (если путь указан к файлу, обрабатываем его)
        if list_path.is_file():
            files_in_dir = [list_path]
        else:
            # Получаем файлы из директории
            files_in_dir = []
            try:
                for dir_file in list_path.iterdir():
                    if dir_file.name.startswith("."):
                        continue
                    files_in_dir.append(dir_file)
            except PermissionError as e:
                raise e

        # Сортируем файлы по имени
        files_in_dir.sort(key=lambda x: x.name, reverse=False)

        if long:
            detailed_list(files_in_dir)
        else:
            # Простой вывод с вашими оригинальными доктринами
            for dir_file in files_in_dir:
                try:
                    # Один вызов stat для определения типа файла
                    file_stat = dir_file.stat()

                    if stat.S_ISDIR(file_stat.st_mode):
                        print(f"{dir_file.name}/")
                    elif stat.S_ISLNK(file_stat.st_mode):
                        print(f"{dir_file.name}@")
                    elif os.access(dir_file, os.X_OK):
                        print(f"{dir_file.name}*")
                    else:
                        print(dir_file.name)

                except OSError as e:
                    logging.warning(e)
                    raise e
                except Exception as e:
                    raise e

    except Exception as e:
        raise e


def ls_args_parse(args: list[str]) -> dict[str, object]:
    """Парсит аргументы команды ls и возвращает их наличие/отсутствие."""
    args_value = {
        'path': '',
        'long': False
    }
    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith("-"):  # с "-" начинаются флаги, у нас только l :(
            if 'l' in args[i]:
                args_value['long'] = True
        else:
            if arg.startswith("'") and arg.endswith("'"): # Остается только path
                args_value["path"] = arg[1:-1]
        i += 1
    return args_value
