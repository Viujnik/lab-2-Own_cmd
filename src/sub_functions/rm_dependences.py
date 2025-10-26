import os


# Здесь собраны функции, необходимые основной функции - rm, чтобы не загрязнять и так грязный main

def rm_args_parse(args: list[str]) -> dict[str, object]:
    """Парсит аргументы команды rm и смотрит, какие переданы, а какие нет"""
    parsed_args = {
        "r_flag": False,
        "path": ''
    }
    i = 0
    while i < len(args):
        cur_arg = args[i]
        if cur_arg.startswith("-"):
            if cur_arg == "-r":
                parsed_args["r_flag"] = True
        else:
            parsed_args["path"] = os.path.normpath(args[i])
        i += 1
    if not parsed_args["path"]:
        error_msg = "Пустой аргумент пути/файла для команды mv."
        raise Exception(error_msg)
    return parsed_args
