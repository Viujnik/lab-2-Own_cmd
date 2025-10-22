import logging
import os
from os import stat_result
from pathlib import Path
from datetime import datetime
import stat


# Здесь собраны функции, необходимые основной функции - ls, чтобы не загрязнять и так грязный main

def check_access_rights(file: stat_result) -> str:
    """Возвращает права доступа для файла"""
    rights = stat.filemode(file.st_mode)
    return str(rights)[-9:]


def detailed_list(files: list[Path]) -> None:
    """Детальный вывод для флага <-l>"""
    for file in files:
        try:
            if isinstance(file, Path):
                file_stat = file.stat()
                file_name = file.name
            else:
                file_stat = Path(file).stat()
                file_name = file
            rights = check_access_rights(file_stat)  # Информация о правах доступа
            links_cnt = file_stat.st_nlink  # Кол-во файлов, на которые ссылается символическая ссылка
            file_uid = file_stat.st_uid  # uid файла
            file_gid = file_stat.st_gid  # gid файла
            file_size = file.stat().st_size  # Размер файла
            mtime = datetime.fromtimestamp(file_stat.st_mtime).strftime(
                '%Y-%m-%d %H:%M:%S')  # Время последнего обновления файла
            if stat.S_ISLNK(file_stat.st_mode):
                linked_file = os.readlink(file if isinstance(file, Path) else Path(file))
                file_name = f"{file_name} -> {linked_file}"
            print(
                f"{rights} {links_cnt:>2} {file_uid} {file_gid} {file_size:>10} {mtime} {file_name}")  # Вывод доп информации
        except Exception as e:
            error = f"Ошибка чтения файла: {file}: {e}"
            logging.error(error)
            raise Exception(error)


def ls_realisation(path: str, long: bool = False) -> None:
    try:
        # Смотри, есть ли аргумент path и приводим его в объект класса Path
        if path:
            list_path = Path(path)
        else:
            list_path = Path.cwd()
        if not list_path.exists():
            error = f"ls: Нет такого файла/директории, {list_path}"
            logging.error(error)
            raise Exception(error)

        files_in_dir = []
        for dir_file in list_path.iterdir():  # Получаем все файлы директории, скрытые файлы пропускаем
            if dir_file.name.startswith("."):
                continue
            files_in_dir.append(dir_file)
        files_in_dir.sort(key=lambda x: x.name, reverse=False)  # Сортируем файлы по имени
        if long:
            detailed_list(files_in_dir)
        else:  # Если есть флаг -l - пользуемся нашей функцией, если нет, то выводим просто файлы
            for dir_file in files_in_dir:
                if dir_file.is_dir():
                    print(f"{dir_file.name}/")
                elif dir_file.is_symlink():
                    print(f"{dir_file.name}@")
                elif os.access(dir_file, os.X_OK):
                    print(f"{dir_file.name}*")
                else:
                    print(dir_file.name)
    except PermissionError:
        error = f"Недостаточно прав для открытия директории {path}"
        logging.error(error)
        raise Exception(error)
    except Exception as e:
        error = f"Неизвестная ошибка: {e}"
        logging.error(error)
        raise Exception(error)


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
        else:  # Остается только path
            args_value["path"] = arg
        i += 1
    return args_value
