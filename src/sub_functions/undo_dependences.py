import argparse
import logging
import shutil
from pathlib import Path
from datetime import datetime
from src.sub_functions.history_dependences import add_to_history, save_history as save_hist, read_history as read_hist

# Здесь собраны функции, необходимые основным функциям - undo, чтобы не загрязнять и так грязный main

# Константы
HISTORY_FILE = ".history"
TRASH_DIR = ".trash"


def init_trash() -> None:
    """Инициализирует папку для корзины"""
    try:
        trash_path = Path(TRASH_DIR).absolute()
        trash_path.mkdir(exist_ok=True)
    except Exception as e:
        raise e


def undo_args_parse(args: list[str]) -> dict[str, int]:
    """Парсит аргументы команды undo"""
    parser = argparse.ArgumentParser(
        prog="undo",
        description="Отменяет step предыдущих команд cp, mv, rm.",
        exit_on_error=False
    )
    parser.add_argument(
        "step",
        nargs="?",
        default=1,
        type=int,
        help="Количество последних команд для отмены"
    )

    try:
        parsed_args = parser.parse_args(args)
        return {"steps": parsed_args.step}
    except SystemExit:
        raise Exception("Ошибка парсинга команды undo: неверный аргумент")


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
            raise Exception(error_msg)

        if len(undoable_commands) < steps:
            error_msg = f"Недостаточно команд для отмены (найдено {len(undoable_commands)}, требуется {steps})"
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
    """Отменяет команду cp удалением скопированного файла"""
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
        src_path_str = undo_data.get("src", "")
        dst_path_str = undo_data.get("dst", "")

        if not src_path_str or not dst_path_str:
            return False

        src_path = Path(src_path_str)
        dst_path = Path(dst_path_str)

        # Проверяем существование перемещенного файла
        if not dst_path.exists():
            return False

        # Проверяем существование исходной директории
        if not src_path.parent.exists():
            return False

        # Если исходный файл уже существует, спрашиваем пользователя
        if src_path.exists():
            response = input(f"Файл {src_path} уже существует. Перезаписать? (y/n): ")
            if response.lower() != 'y':
                return False

        # Перемещаем файл обратно
        shutil.move(str(dst_path), str(src_path))

        # Проверяем результат
        return src_path.exists() and not dst_path.exists()

    except Exception as e:
        logging.error(f"Ошибка при отмене mv: {e}")
        return False


def undo_rm(undo_data: dict) -> bool:
    """Отменяет команду rm - восстанавливает файл из корзины"""
    try:
        original_path = undo_data.get("path")
        trash_path = undo_data.get("trash_path")
        # Проверки на None и тип
        if not original_path or not trash_path:
            return False

        if not isinstance(original_path, str) or not isinstance(trash_path, str):
            return False

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
        raise e


def mv_with_history(src: str, dst: str) -> None:
    """Перемещение с записью в историю"""
    try:
        src_path = Path(src)
        dst_path = Path(dst)

        # Определяем фактический конечный путь
        if dst_path.is_dir():
            actual_dst = dst_path / src_path.name
        else:
            actual_dst = dst_path

        shutil.move(str(src_path), str(dst_path))

        # Добавляем в историю с путями
        undo_data = {
            "src": str(src_path.absolute()),
            "dst": str(actual_dst.absolute())
        }

        add_to_history("mv", [src, dst], undo_data)

    except Exception as e:
        raise e


def rm_with_history(path: str) -> None:
    """Удаление с перемещением в корзину и записью в историю"""
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            error_msg = f"Файл или директория не существует: {path}"
            raise FileNotFoundError(error_msg)

        # Запрос подтверждения удаления
        confirmation = input(
            f"Вы уверены, что хотите удалить {path}? (y - для подтверждения, любой другой символ для прерывания удаления): ")

        if confirmation.lower() != 'y':
            print("Удаление отменено.")
            return

        # Получаем абсолютный пути
        absolute_path = path_obj.absolute()

        # Проверка, что корзина существует
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

        add_to_history("rm", [path], undo_data)

    except Exception as e:
        raise e
