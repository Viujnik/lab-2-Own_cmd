import os
import shlex
import sys
import logging

# Добавляем путь для корректных импортов
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Теперь импортируем модули
from src.sub_functions.undo_dependences import (undo_args_parse, undo_realisation, init_trash, cp_with_history,
                                            mv_with_history, rm_with_history)
from src.sub_functions.history_dependences import history_args_parse, history_realisation, history_mkdir, add_to_history
from src.sub_functions.help_func import help_realisation
from src.sub_functions.grep_dependences import grep_args_parse, grep_realisation
from src.sub_functions.unarchive_dependences import unarchive_args_parse, unarchive_realisation
from src.sub_functions.archive_dependences import archive_args_parse, archive_realisation
from src.sub_functions.rm_dependences import rm_args_parse
from src.sub_functions.cat_dependences import cat_realisation, cat_args_parse
from src.sub_functions.cd_dependences import cd_realisation, cd_args_parse
from src.sub_functions.cp_dependences import cp_args_parse
from src.sub_functions.mv_dependences import mv_args_parse
from src.sub_functions.ls_dependences import ls_args_parse, ls_realisation
from src.sub_functions.logging_func import logging_command, logger, unhandled_exception


history_mkdir()
init_trash()


def input_shell() -> None:
    while True:
        try:
            user_input = input(f"{os.getcwd()}> ").strip()
            if not user_input:
                continue
            args = shlex.split(user_input)
            command = args[0]
            logging_command(command, args[1:])

            # Добавляем команду в историю (кроме самих history и undo и команд, которые записываются в историю при реализации)
            if command not in ["history", "undo", "cp", "mv", "rm"]:
                add_to_history(command, args[1:], None)
            # Смотрим какая команда введена
            match command:
                case "ls":
                    args_value = ls_args_parse(args[1:])
                    ls_realisation(path=str(args_value["path"]), long=bool(args_value["long"]))
                case "cd":
                    arg_value = cd_args_parse(args[1:])
                    cd_realisation(str(arg_value))
                case "cat":
                    arg_value = cat_args_parse(args[1:])
                    cat_realisation(str(arg_value))
                case "cp":
                    cp_args = cp_args_parse(args[1:])
                    # Используем версию с историей для поддержки undo
                    cp_with_history(cp_args[0], str(cp_args[1]))
                case "mv":
                    mv_args = mv_args_parse(args[1:])
                    path_from, path_to = mv_args
                    mv_with_history(path_from, path_to)
                case "rm":
                    rm_args = rm_args_parse(args[1:])
                    # Используем версию с историей для поддержки undo
                    rm_with_history(str(rm_args['path']))
                case "zip":
                    archive_realisation(args)
                case "tar":
                    tar_args = archive_args_parse(args)
                    archive_realisation(tar_args)
                case "unzip":
                    unzip_args = unarchive_args_parse(args)
                    unarchive_realisation(unzip_args)
                case "untar":
                    untar_args = unarchive_args_parse(args)
                    unarchive_realisation(untar_args)
                case "grep":
                    grep_args = grep_args_parse(args[1:])
                    grep_realisation(grep_args)
                case "history":
                    history_args = history_args_parse(args[1:])
                    history_realisation(history_args)
                case "undo":
                    undo_args = undo_args_parse(args[1:])
                    undo_realisation(undo_args)
                case "help":
                    help_realisation()
                case "exit":
                    break
                case _:
                    error_msg = f"Неизвестная команда: {command}"
                    logging.error(error_msg)
                    raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Ошибка: {e}"
            logging.error(error_msg)
            print(error_msg)  # Выводим ошибку пользователю, но не прерываем работу


sys.excepthook = unhandled_exception

if __name__ == "__main__":
    logger.info("Запуск приложения")
    if len(sys.argv) == 1:
        input_shell()
