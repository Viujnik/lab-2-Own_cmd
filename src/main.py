import os
import shlex
import sys
import logging
import zipfile

from sub_functions.unarchive_dependences import unarchive_args_parse, unarchive_realisation
from sub_functions.archive_dependences import archive_args_parse, archive_realisation

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from sub_functions.rm_dependences import rm_args_parse, rm_realisation
from sub_functions.cat_dependences import cat_realisation, cat_args_parse
from sub_functions.cd_dependences import cd_realisation, cd_args_parse
from sub_functions.cp_dependences import cp_args_parse, cp_realisation
from sub_functions.mv_dependences import mv_args_parse, mv_realisation
from sub_functions.ls_dependences import ls_args_parse, ls_realisation
from sub_functions.logging_func import logging_command, logger, unhandled_exception

with zipfile.ZipFile("test.zip", "w") as zipf:
    zipf.writestr("test.txt", "This is a test")


def input_shell() -> None:
    while True:
        try:
            user_input = input(f"{os.getcwd()}> ").strip()
            if not user_input:
                continue
            args = shlex.split(user_input, posix=False)
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
            elif command == "rm":
                rm_args = rm_args_parse(args[1:])
                rm_realisation(rm_args)
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
                pass
            elif command == "exit" or "stop_machina":
                break
            else:
                error_msg = f"Неизвестная команда: {command}"
                logging.error(error_msg)
                print(error_msg)
        except KeyboardInterrupt:
            print("Выход из интерактивного режима")
            break
        except Exception as e:
            error_msg = f"Ошибка: {e}"
            logging.error(error_msg)
            print(error_msg)


sys.excepthook = unhandled_exception

if __name__ == "__main__":
    logger.info("Запуск приложения")
    if len(sys.argv) == 1:
        input_shell()
