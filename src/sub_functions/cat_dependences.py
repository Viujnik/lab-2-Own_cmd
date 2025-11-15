import argparse
from pathlib import Path

# Здесь собраны функции, необходимые основной функции - cat, чтобы не загрязнять и так грязный main


def cat_args_parse(args: list[str]) -> Path:
    """Проверяет аргумент path функции cat. Возвращает этот путь класса Path или ошибку."""
    parser = argparse.ArgumentParser(prog="cat", description="Просмотр содержимого файла", exit_on_error=False)
    parser.add_argument("file", help="Файл для просмотра")
    try:
        parsed_args = parser.parse_args(args)
        return Path(parsed_args.file)
    except argparse.ArgumentError as e:
        raise Exception(f"Ошибка парсинга команды cat: {e}")



def cat_realisation(path: str) -> None:
    """Читает и выводит содержимое файла"""
    file_path = Path(path)
    with file_path.open("r", encoding='utf-8') as file:
        print(file.read())
