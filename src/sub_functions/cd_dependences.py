import logging
import os
from pathlib import Path


def cd_args_parse(args: list[str]) -> Path:
    """Проверяет аргумент path функции cd. Возвращает этот путь класса Path или None при ошибке."""
    if not args:  # Проверяем, что args не пустой
        error = "Для команды cd ожидается аргумент - path"
        logging.error(error)
        print(error)


    path_str = args[0]
    if not path_str:  # Проверяем, что путь не пустая строка
        error = "Путь не может быть пустой строкой"
        logging.error(error)
        print(error)

    if path_str == "~":
        return Path(os.path.expanduser("~"))

    path = Path(path_str)

    # Проверяем существование пути
    if not path.exists():
        error = f"cd: {path}: No such file or directory"
        logging.error(error)
        print(error)

    # Проверяем, что это директория (не файл)
    if not path.is_dir():
        error = f"cd: {path}: Not a directory"
        logging.error(error)
        print(error)

    return path


def cd_realisation(path: str) -> None:
    """Функция для смены директории для аргумента path. Тут всё очевидно."""
    try:
        if path == "~":
            new_path = os.path.expanduser("~")
            os.chdir(new_path)
        else:
            # Получаем абсолютный путь для ясности
            abs_path = os.path.abspath(path)
            os.chdir(abs_path)

    except PermissionError as e:
        error = f"cd: {path}: Отказано в доступе: {e}"
        logging.error(error)
        print(error)
    except FileNotFoundError as e:
        error = f"cd: {path}: No such file or directory: {e}"
        logging.error(error)
        print(error)
    except NotADirectoryError as e:
        error = f"cd: {path}: Not a directory: {e}"
        logging.error(error)
        print(error)
    except Exception as e:
        error = f"cd: {path}: Unexpected error: {e}"
        logging.error(error)
        print(error)
