from pathlib import Path


# Здесь собраны функции, необходимые основной функции - cp, чтобы не загрязнять и так грязный main


def cp_args_parse(args: list[str]) -> list[str]:
    if len(args) == 2:
        path_from = args[0]
        if path_from.startswith("'") and path_from.endswith("'"):
            path_from = path_from[1:-1]
        path_from_path = Path(path_from)
        path_to = args[1]
        if path_to.startswith("'") and path_to.endswith("'"):
            path_to = path_to[1:-1]
        path_to_path = Path(path_to)
        if not path_from_path.exists():
            error = f"Файл {path_from_path} не найден."
            raise FileNotFoundError(error)
        if not path_to_path.exists():
            error = f"Директория {path_to_path} не найдена."
            raise NotADirectoryError(error)
        return [path_from, path_to]
    else:
        error = "Введите 2 аргумента: файл и дерикторию."
        raise Exception(error)
