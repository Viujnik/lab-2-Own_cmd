import logging
from pathlib import Path


# Здесь собраны функции, необходимые основной функции - cat, чтобы не загрязнять и так грязный main

def cat_args_parse(args: list[str]) -> Path | None:
    """Проверяет аргумент path функции cat. Возвращает этот путь класса Path или None при ошибке."""
    if args[0]:
        arg = Path(args[0])
        if arg.is_dir() or arg.is_symlink() or (not arg.exists()):  # Всякий мусор, кроме файла, нам не нужен
            error = "Для команды cat нужно передать файл или путь к файлу"
            print(error)
            logging.error(error)
            return None
        else:
            return arg

    else:
        error = "Для команды cat ожидается 2-ой аргумент - файл или путь к файлу"
        print(error)
        logging.error(error)
        return None


def cat_realisation(path: str) -> None:
    file_path = Path(path)
    with file_path.open("r", encoding='utf-8') as file:
        print(file.read())
