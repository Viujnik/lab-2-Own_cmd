import argparse


# Здесь собраны функции, необходимые основной функции - rm, чтобы не загрязнять и так грязный main

def rm_args_parse(args: list[str]) -> dict[str, object]:
    """Парсит аргументы команды rm"""
    parser = argparse.ArgumentParser(
        prog="rm",
        description="Удаляет файл или директорию",
        exit_on_error=False
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Рекурсивное удаление директорий"
    )
    parser.add_argument("path", help="Путь к удаляемому файлу или директории")

    try:
        parsed_args = parser.parse_args(args)
        return {
            "recursive": parsed_args.recursive,
            "path": parsed_args.path
        }
    except SystemExit:
        raise Exception("Ошибка парсинга команды rm: требуется путь к файлу или директории")
