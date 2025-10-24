from pathlib import Path


def cat_args_parse(args: list[str]) -> Path:
    """Проверяет аргумент path функции cat. Возвращает этот путь класса Path или None при ошибке."""
    if args and args[0]:
        arg = Path(args[0])
        if not arg.exists():
            raise FileNotFoundError(f"Файл {arg} не существует")
        elif arg.is_dir() or arg.is_symlink():
            error = "Для команды cat нужно передать файл или путь к файлу"
            raise Exception(error)
        else:
            return arg
    else:
        error = "Для команды cat ожидается 2-ой аргумент - файл или путь к файлу"
        raise Exception(error)


def cat_realisation(path: str) -> None:
    """Читает и выводит содержимое файла"""
    file_path = Path(path)
    with file_path.open("r", encoding='utf-8') as file:
        print(file.read())