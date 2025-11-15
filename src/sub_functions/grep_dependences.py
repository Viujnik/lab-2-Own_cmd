import argparse
import re
from pathlib import Path


# Здесь собраны функции, необходимые основной функции - grep, чтобы не загрязнять и так грязный main


def grep_args_parse(args: list[str]):
    parser = argparse.ArgumentParser(prog="grep", description="Поиск текста в файлах", exit_on_error=False)
    parser.add_argument("-r", "--recursive", action="store_true", help="Рекурсивный поиск в директории")
    parser.add_argument("-i", "--ignore-case", action="store_true", help="Игнорировать регистр")
    parser.add_argument("pattern", help="Шаблон для поиска")
    parser.add_argument("path", help="Файл или директория для поиска")
    try:
        return {
            "path": parser.parse_args(args).path,
            "recursive": parser.parse_args(args).recursive,
            "ignore_case": parser.parse_args(args).ignore_case,
            "pattern": parser.parse_args(args).pattern,
        }
    except argparse.ArgumentError as e:
        raise Exception(f"Ошибка парсинга команды grep: {e}")




def grep_realisation(args: dict[str, str]) -> None:
    pattern = str(args["pattern"])
    path = str(args["path"])
    recursive = args.get("recursive", False)
    ignore_case = args.get("ignore_case", False)
    flags = re.IGNORECASE if ignore_case else 0

    try:
        regex = re.compile(pattern, flags)
    except re.error as e:
        raise ValueError(f"Ошибка в шаблоне: {e}")

    def search_in_file(file_to_search: Path) -> list[tuple]:
        result_of_search = []
        try:
            with open(file_to_search, 'r', encoding='utf-8', errors='ignore') as f:
                for line_number, line in enumerate(f, 1):
                    if regex.search(line):
                        cleaned_line = line.strip()
                        result_of_search.append((str(file_to_search), line_number, cleaned_line))
        except (IOError, PermissionError) as err:
            print(f"Ошибка чтения файла {file_to_search}: {err}")
        return result_of_search

    def search_in_directory(dir_path: Path) -> list[tuple]:
        results_of_search = []
        try:
            for file in dir_path.iterdir():
                if file.is_file():
                    results_of_search.extend(search_in_file(file))
                elif file.is_dir() and recursive:
                    results_of_search.extend(search_in_directory(file))
        except (IOError, PermissionError) as err:
            print(f"Ошибка доступа к директории {dir_path}: {err}")
        return results_of_search

    path_obj = Path(path)
    results = []

    if path_obj.is_file():
        results = search_in_file(path_obj)
    elif path_obj.is_dir():
        if recursive:
            results = search_in_directory(path_obj)
        else:
            for item in path_obj.iterdir():
                if item.is_file():
                    results.extend(search_in_file(item))
    else:
        raise FileNotFoundError(f"Путь '{path}' не существует")

    for file_path, line_num, line_content in results:
        print(f"{file_path}:{line_num}:{line_content}")
