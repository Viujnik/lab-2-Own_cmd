import logging
import shutil
from pathlib import Path
from datetime import datetime
from src.sub_functions.history_dependences import add_to_history, save_history as save_hist, read_history as read_hist

# Константы
HISTORY_FILE = ".history"
TRASH_DIR = ".trash"


def init_trash() -> None:
    """Инициализирует папку для корзины"""
    try:
        trash_path = Path(TRASH_DIR).absolute()
        trash_path.mkdir(exist_ok=True)
    except Exception as e:
        logging.error(f"Ошибка инициализации корзины: {e}")
        raise e


def undo_args_parse(args: list[str]) -> dict[str, int]:
    """Парсит аргументы команды undo"""
    args_value = {
        "steps": 1
    }

    for arg in args:
        if arg.isdigit():
            args_value["steps"] = int(arg)
        elif arg.startswith('-'):
            error_msg = f"undo: неверная опция '{arg}'"
            logging.error(error_msg)
            raise ValueError(error_msg)

    return args_value


def read_history() -> list:
    """Читает историю команд из файла"""
    return read_hist()


def save_history(history: list) -> None:
    """Сохраняет историю команд"""
    save_hist(history)


def undo_realisation(args: dict[str, int]) -> None:
    """Основная реализация функции undo"""
    try:
        steps = args["steps"]

        # Читаем историю
        history = read_history()

        if not history:
            info_msg = "История команд пуста - нечего отменять"
            logging.info(info_msg)
            raise Exception(info_msg)

        # Ищем последние команды cp, mv, rm для отмены
        undoable_commands = []
        for record in reversed(history):
            if record["command"] in ["cp", "mv", "rm"] and record.get("undo_data"):
                undoable_commands.append(record)
            if len(undoable_commands) >= steps:
                break

        if not undoable_commands:
            error_msg = "Нет команд для отмены (поддерживаются только cp, mv, rm)"
            logging.error(error_msg)
            raise Exception(error_msg)

        if len(undoable_commands) < steps:
            error_msg = f"Недостаточно команд для отмены (найдено {len(undoable_commands)}, требуется {steps})"
            logging.error(error_msg)
            raise Exception(error_msg)

        # Отменяем команды
        success_count = 0
        for record in undoable_commands:
            success = undo_command(record)
            if success:
                success_count += 1

        # Удаляем отмененные команды из истории
        if success_count > 0:
            remaining_history = [r for r in history if r not in undoable_commands]
            save_history(remaining_history)

    except Exception as e:
        error_msg = f"Ошибка при отмене команды: {e}"
        logging.error(error_msg)
        raise e


def undo_command(record: dict) -> bool:
    """Отменяет конкретную команду"""
    command = record["command"]
    try:
        undo_data = record.get("undo_data", {})

        if command == "cp":
            return undo_cp(undo_data)
        elif command == "mv":
            return undo_mv(undo_data)
        elif command == "rm":
            return undo_rm(undo_data)
        else:
            return False

    except Exception as e:
        logging.error(f"Ошибка при отмене команды {command}: {e}")
        return False


def undo_cp(undo_data: dict) -> bool:
    """Отменяет команду cp - удаляет скопированный файл"""
    try:
        src_path = Path(undo_data.get("src", ""))
        dst_path = Path(undo_data.get("dst", ""))

        if not dst_path.exists():
            return False

        # Если dst является директорией, то нужно удалить файл внутри неё с именем исходного файла
        if dst_path.is_dir():
            # Определяем имя исходного файла
            original_filename = src_path.name
            # Формируем полный путь к скопированному файлу
            copied_file_path = dst_path / original_filename

            if copied_file_path.exists():
                copied_file_path.unlink()
                return True
            else:
                return False
        else:
            # Если dst является файлом, просто удаляем его
            dst_path.unlink()
            return True

    except Exception as e:
        logging.error(f"Ошибка при отмене cp: {e}")
        return False


def undo_mv(undo_data: dict) -> bool:
    """Отменяет команду mv - возвращает файл на исходное место"""
    try:
        src_path = undo_data.get("src")
        dst_path = undo_data.get("dst")
        if dst_path and Path(dst_path).exists() and src_path:
            shutil.move(dst_path, src_path)
            return True
        return False
    except Exception as e:
        logging.error(f"Ошибка при отмене mv: {e}")
        raise e


def undo_rm(undo_data: dict) -> bool:
    """Отменяет команду rm - восстанавливает файл из корзины"""
    try:
        original_path = undo_data.get("path")
        trash_path = undo_data.get("trash_path")

        trash_file = Path(trash_path)
        original_file = Path(original_path)

        # Создаем родительские директории, если нужно
        original_file.parent.mkdir(parents=True, exist_ok=True)

        # Восстанавливаем файл
        shutil.move(str(trash_file), str(original_file))

        # Проверяем успешность восстановления
        if original_file.exists():
            return True
        else:
            return False

    except Exception as e:
        logging.error(f"Ошибка при отмене rm: {e}")
        raise e

def cp_with_history(src: str, dst: str) -> None:
    """Копирование с записью в историю"""
    try:
        src_path = Path(src)
        dst_path = Path(dst)

        if src_path.is_file():
            # Если dst является директорией, копируем файл в эту директорию
            if dst_path.is_dir():
                final_dst_path = dst_path / src_path.name
                shutil.copy2(src, final_dst_path)
                actual_dst = str(final_dst_path)
            else:
                shutil.copy2(src, dst)
                actual_dst = dst
        else:
            shutil.copytree(src, dst)
            actual_dst = dst

        # Добавляем в историю с данными для отмены
        undo_data = {
            "src": str(src_path.absolute()),
            "dst": actual_dst if src_path.is_file() and dst_path.is_dir() else str(dst_path.absolute())
        }

        add_to_history("cp", [src, dst], undo_data)

    except Exception as e:
        logging.error(f"Ошибка при копировании: {e}")
        raise e


def mv_with_history(src: str, dst: str) -> None:
    """Перемещение с записью в историю"""
    try:
        src_path = Path(src)
        dst_path = Path(dst)

        shutil.move(src, dst)

        # Добавляем в историю с данными для отмены
        undo_data = {
            "src": str(src_path.absolute()),
            "dst": str(dst_path.absolute())
        }
        add_to_history("mv", [src, dst], undo_data)

    except Exception as e:
        logging.error(f"Ошибка при перемещении: {e}")
        raise e


def rm_with_history(path: str) -> None:
    """Удаление с перемещением в корзину и записью в историю"""
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            error_msg = f"Файл или директория не существует: {path}"
            logging.error(error_msg)
            raise FileNotFoundError(error_msg)

        # Получаем абсолютные пути
        absolute_path = path_obj.absolute()

        # Убедимся, что корзина существует
        trash_dir = Path(TRASH_DIR).absolute()
        trash_dir.mkdir(exist_ok=True)

        # Создаем уникальное имя в корзине
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        trash_name = f"{timestamp}_{path_obj.name}"
        trash_path = trash_dir / trash_name

        # Перемещаем в корзину
        shutil.move(str(absolute_path), str(trash_path))

        # Добавляем в историю с данными для отмены
        undo_data = {
            "path": str(absolute_path),
            "trash_path": str(trash_path)
        }

        from src.sub_functions.history_dependences import add_to_history
        add_to_history("rm", [path], undo_data)

    except Exception as e:
        logging.error(f"Ошибка при удалении {path}: {e}")
        raise e
