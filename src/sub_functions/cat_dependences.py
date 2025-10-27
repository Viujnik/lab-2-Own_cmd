from pathlib import Path

# Здесь собраны функции, необходимые основной функции - cat, чтобы не загрязнять и так грязный main


def cat_args_parse(args: list[str]) -> Path:
    """Проверяет аргумент path функции cat. Возвращает этот путь класса Path или ошибку."""
    if args and args[0]:
        arg = args[0]
        if arg[0].startswith("'") and arg[0].endswith("'"):
            arg = arg[1:-1]
        arg_path = Path(arg)
        if not arg_path.exists():
            raise FileNotFoundError(f"Файл {arg_path} не существует")
        elif arg_path.is_dir() or arg_path.is_symlink():
            error = "Для команды cat нужно передать файл или путь к файлу"
            raise Exception(error)
        else:
            return arg_path
    else:
        error = "Для команды cat ожидается 2-ой аргумент - файл или путь к файлу"
        raise Exception(error)


def cat_realisation(path: str) -> None:
    """Читает и выводит содержимое файла"""
    file_path = Path(path)
    with file_path.open("r", encoding='utf-8') as file:
        print(file.read())
