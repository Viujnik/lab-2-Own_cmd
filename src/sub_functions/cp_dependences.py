import argparse


# Здесь собраны функции, необходимые основной функции - cp, чтобы не загрязнять и так грязный main


def cp_args_parse(args: list[str]) -> list[str]:
    """Парсит аргументы команды cp"""
    parser = argparse.ArgumentParser(
        prog="cp",
        description="Копирует файл из path_from в path_to",
        exit_on_error=False
    )
    parser.add_argument("path_from", help="Путь откуда копировать")
    parser.add_argument("path_to", help="Путь куда копировать")

    try:
        parsed_args = parser.parse_args(args)
        return [parsed_args.path_from, parsed_args.path_to]
    except SystemExit:
        raise Exception("Ошибка парсинга команды cp: требуется 2 аргумента - путь_откуда и путь_куда")
