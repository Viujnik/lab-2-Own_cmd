from pathlib import Path


# Здесь собраны функции, необходимые основной функции - cp, чтобы не загрязнять и так грязный main


def cp_args_parse(args: list[str]) -> list[str]:
    if len(args) == 2:
        path_from = Path(args[0])
        path_to = Path(args[1])
        if not path_from.exists():
            error = f"Файл {path_from} не найден."
            raise FileNotFoundError(error)
        if not path_to.exists():
            error = f"Директория {path_from} не найдена."
            raise NotADirectoryError(error)
        return [str(path_from), str(path_to)]
    else:
        error = "Введите 2 аргумента: файл и дерикторию."
        raise Exception(error)
