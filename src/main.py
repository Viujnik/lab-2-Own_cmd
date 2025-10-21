import os
import shlex
import sys
import logging
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from sub_functions.undo_dependences import (undo_args_parse, undo_realisation, init_trash, cp_with_history,
                                            mv_with_history, rm_with_history, read_history)
from src.sub_functions.history_dependences import history_args_parse, history_realisation, history_mkdir, add_to_history
from sub_functions.help_func import help_realisation
from sub_functions.grep_dependences import grep_args_parse, grep_realisation
from sub_functions.unarchive_dependences import unarchive_args_parse, unarchive_realisation
from sub_functions.archive_dependences import archive_args_parse, archive_realisation
from sub_functions.rm_dependences import rm_args_parse
from sub_functions.cat_dependences import cat_realisation, cat_args_parse
from sub_functions.cd_dependences import cd_realisation, cd_args_parse
from sub_functions.cp_dependences import cp_args_parse
from sub_functions.mv_dependences import mv_args_parse
from sub_functions.ls_dependences import ls_args_parse, ls_realisation
from sub_functions.logging_func import logging_command, logger, unhandled_exception

history_mkdir()
init_trash()


def input_shell() -> None:
    while True:
        try:
            user_input = input(f"{os.getcwd()}> ").strip()
            if not user_input:
                continue
            args = shlex.split(user_input, posix=False)
            command = args[0]
            logging_command(command, args[1:])

            # Добавляем команду в историю (кроме самих history и undo)
            if command not in ["history", "undo", "cp", "mv", "rm"]:
                add_to_history(command, args[1:])

            # Смотрим какая команда введена
            if command == "ls":
                args_value = ls_args_parse(args[1:])
                ls_realisation(path=str(args_value["path"]), long=bool(args_value["long"]))
            elif command == "cd":
                arg_value = cd_args_parse(args[1:])
                cd_realisation(str(arg_value))
            elif command == "cat":
                arg_value = cat_args_parse(args[1:])
                cat_realisation(str(arg_value))
            elif command == "cp":
                cp_args = cp_args_parse(args[1:])
                # Используем версию с историей для поддержки undo
                cp_with_history(cp_args[0], str(cp_args[1]))
            elif command == "mv":
                mv_args = mv_args_parse(args[1:])
                path_from, path_to = mv_args
                mv_with_history(path_from, path_to)
            elif command == "rm":
                rm_args = rm_args_parse(args[1:])
                # Используем версию с историей для поддержки undo
                rm_with_history(str(rm_args['path']))
            elif command == "zip":
                zip_args = archive_args_parse(args)
                archive_realisation(zip_args)
            elif command == "tar":
                tar_args = archive_args_parse(args)
                archive_realisation(tar_args)
            elif command == "unzip":
                unzip_args = unarchive_args_parse(args)
                unarchive_realisation(unzip_args)
            elif command == "untar":
                untar_args = unarchive_args_parse(args)
                unarchive_realisation(untar_args)
            elif command == "grep":
                grep_args = grep_args_parse(args[1:])
                grep_realisation(grep_args)
            elif command == "history":
                history_args = history_args_parse(args[1:])
                history_realisation(history_args)
            elif command == "undo":
                undo_args = undo_args_parse(args[1:])
                undo_realisation(undo_args)
            elif command == "debug_history":
                history = read_history()
                print("Диагностика истории:")
                for record in history:
                    print(f"- {record['command']}: {record.get('undo_data', {})}")
            elif command == "help":
                help_realisation()
            else:
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
