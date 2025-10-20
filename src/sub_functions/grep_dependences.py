# Здесь собраны функции, необходимые основным функциям - unzip\untar, чтобы не загрязнять и так грязный main
import logging
import re
from pathlib import Path


def grep_args_parse(args: list[str]) -> dict[str, str]:
    if len(args) < 2:
        error_msg = "Используйте верный синтаксис: grep [OPTIONS] PATTERN PATH"
        raise SyntaxError(error_msg)
    args_value = {
        "options": '',
        "pattern": '',
        "path": ''
    }
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ['-r', '-i']:
            args_value["options"] += arg + ' '
        elif args_value["pattern"] is None:
            args_value["pattern"] = arg
        elif args_value["path"] is None:
            args_value["path"] = arg
        i += 1
    if not (args_value["pattern"] or args_value["path"]):
        error_msg = "необходимо указать PATTERN и PATH"
        raise SyntaxError(error_msg)
    return args_value


def grep_realisation(args: dict[str, str]) -> None:
    options = args["options"].split()
    pattern = str(args["pattern"])
    path = str(args["path"])
    recursive = '-r' in options
    ignore_case = '-i' in options
    flags = re.IGNORECASE if ignore_case else 0
    try:
        regex = re.compile(pattern, flags)
    except re.error as e:
        print(f"Ошибка в шаблоне: {e}")

    results = []

    def search_in_file(file_path: Path) -> None:
        """Поиск шаблона в одном файле"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    if regex.search(line):
                        # Убираем лишние пробелы и переносы строк
                        cleaned_line = line.strip()
                        results.append((str(file_path), line_num, cleaned_line))
        except (IOError, PermissionError) as err:
            error_msg = f"Ошибка чтения файла {file_path}: {err}"
            logging.error(error_msg)
            raise Exception(error_msg)

    def search_in_directory(dir_path: Path) -> None:
        """Рекурсивный поиск в директории"""
        try:
            for file in Path(dir_path).iterdir():
                if file.is_file():
                    search_in_file(file)
                elif file.is_dir() and recursive:
                    search_in_directory(file)
        except (IOError, PermissionError) as err:
            print(f"Ошибка доступа к директории {dir_path}: {err}")

    # Определяем тип пути и начинаем поиск
    path_obj = Path(path)

    if path_obj.is_file():
        search_in_file(path_obj)
    elif path_obj.is_dir():
        if recursive:
            search_in_directory(path_obj)
        else:
            # Без рекурсии ищем только в файлах непосредственно в указанной директории
            for item in path_obj.iterdir():
                if item.is_file():
                    search_in_file(item)
    else:
        print(f"Ошибка: путь '{path}' не существует")
