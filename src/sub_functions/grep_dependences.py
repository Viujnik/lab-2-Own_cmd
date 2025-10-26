import re
from pathlib import Path


# Здесь собраны функции, необходимые основной функции - grep, чтобы не загрязнять и так грязный main


def grep_args_parse(args: list[str]) -> dict[str, str]:
    if len(args) < 2:
        raise SyntaxError("Используйте верный синтаксис: grep [OPTIONS] PATTERN PATH")

    args_value = {"options": '', "pattern": '', "path": ''}
    i = 0

    while i < len(args):
        arg = args[i]
        if arg in ['-r', '-i']:
            args_value["options"] += arg + ' '
        elif not args_value["pattern"]:
            args_value["pattern"] = arg
        elif not args_value["path"]:
            args_value["path"] = arg
        i += 1

    if not args_value["pattern"] or not args_value["path"]:
        raise SyntaxError("Необходимо указать PATTERN и PATH")

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
