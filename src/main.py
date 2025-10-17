import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sub_functions.cat_dependences import cat_realisation, cat_args_parse
from sub_functions.cd_dependences import cd_realisation, cd_args_parse
from sub_functions.cp_dependences import cp_args_parse, cp_realisation
from sub_functions.mv_dependences import mv_args_parse, mv_realisation
from sub_functions.ls_dependences import ls_args_parse, ls_realisation
from sub_functions.logging_func import logging_command, logger, unhandled_exception


def input_shell() -> None:
    while True:
        try:
            user_input = input(f"{os.getcwd()}> ").strip()
            if not user_input:
                continue
            args = user_input.split()
            command = args[0]
            logging_command(command, args[1:])
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
                cp_realisation(cp_args)
            elif command == "mv":
                mv_args = mv_args_parse(args[1:])
                path_from, path_to = mv_args
                mv_realisation(path_from, path_to)
            else:
                print(f"Неизвестная команда: {command}")
        except KeyboardInterrupt:
            print("Выход из интерактивного режима")
            break
        except Exception as e:
            error_msg = f"Ошибка: {e}"
            print(error_msg)





sys.excepthook = unhandled_exception

if __name__ == "__main__":
    logger.info("Запуск приложения")
    if len(sys.argv) == 1:
        input_shell()
