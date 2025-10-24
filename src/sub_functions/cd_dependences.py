import logging
import os
from pathlib import Path


def cd_args_parse(args: list[str]) -> Path:
    """Проверяет аргумент path функции cd. Возвращает этот путь класса Path или None при ошибке."""
    if not args:  # Проверяем, что args не пустой
        error = "Для команды cd ожидается аргумент - path"
        raise Exception(error)

    path_str = args[0]
    if not path_str:  # Проверяем, что путь не пустая строка
        error = "Путь не может быть пустой строкой"
        raise Exception(error)

    if path_str == "~":
        return Path(os.path.expanduser("~"))

    path = Path(path_str)

    # Проверяем существование пути
    if not path.exists():
        error_msg = f"Директория {path} не существует"
        raise Exception(error_msg)

    # Проверяем, что это директория (не файл)
    if not path.is_dir():
        error_msg = f"{path} не является директорией"
        raise Exception(error_msg)

    return path


def cd_realisation(path: str) -> None:
    """Функция для смены директории для аргумента path. Тут всё очевидно."""
    try:
        if path == "~":
            new_path = os.path.expanduser("~")
            os.chdir(new_path)
        else:
            # Получаем абсолютный путь
            abs_path = os.path.abspath(path)
            os.chdir(abs_path)

    except PermissionError as e:
        logging.error(e)
        raise e
    except Exception as e:
        logging.error(e)
        raise e