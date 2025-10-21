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
        print(f"DEBUG: Корзина инициализирована: {trash_path}")
    except Exception as e:
        logging.error(f"Ошибка инициализации корзины: {e}")
        raise


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
            print("История команд пуста - нечего отменять")
            return

        # Ищем последние команды cp, mv, rm для отмены
        undoable_commands = []
        for record in reversed(history):
            if record["command"] in ["cp", "mv", "rm"] and record.get("undo_data"):
                undoable_commands.append(record)
            if len(undoable_commands) >= steps:
                break

        print(f"DEBUG undo_realisation: найдено команд для отмены: {len(undoable_commands)}")
        for i, record in enumerate(undoable_commands):
            print(f"DEBUG undo_realisation: команда {i}: {record['command']} {record['args']}")
            print(f"DEBUG undo_realisation: undo_data: {record.get('undo_data')}")

        if not undoable_commands:
            print("Нет команд для отмены (поддерживаются только cp, mv, rm)")
            return

        if len(undoable_commands) < steps:
            print(f"Недостаточно команд для отмены (найдено {len(undoable_commands)}, требуется {steps})")
            return

        # Отменяем команды
        success_count = 0
        for record in undoable_commands:
            success = undo_command(record)
            if success:
                print(f"✓ Отменена команда: {record['command']} {' '.join(record['args'])}")
                success_count += 1
            else:
                print(f"✗ Не удалось отменить команду: {record['command']} {' '.join(record['args'])}")

        # Удаляем отмененные команды из истории
        if success_count > 0:
            remaining_history = [r for r in history if r not in undoable_commands]
            save_history(remaining_history)
            print(f"Успешно отменено команд: {success_count}")

    except Exception as e:
        error_msg = f"Ошибка при отмене команды: {e}"
        logging.error(error_msg)
        print(error_msg)


def undo_command(record: dict) -> bool:
    """Отменяет конкретную команду"""
    command = record["command"]
    try:
        undo_data = record.get("undo_data", {})

        print(f"DEBUG: Отменяем {command} с данными: {undo_data}")

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
        print(f"DEBUG: Ошибка отмены {command}: {e}")
        return False


def undo_cp(undo_data: dict) -> bool:
    """Отменяет команду cp - удаляет скопированный файл"""
    try:
        src_path = Path(undo_data.get("src", ""))
        dst_path = Path(undo_data.get("dst", ""))

        print(f"DEBUG: undo_cp - src: {src_path}, dst: {dst_path}")
        print(f"DEBUG: dst exists: {dst_path.exists()}, is_file: {dst_path.is_file()}, is_dir: {dst_path.is_dir()}")

        if not dst_path.exists():
            print(f"DEBUG: Файл назначения не существует: {dst_path}")
            return False

        # Если dst является директорией, то нужно удалить файл внутри неё с именем исходного файла
        if dst_path.is_dir():
            # Определяем имя исходного файла
            original_filename = src_path.name
            # Формируем полный путь к скопированному файлу
            copied_file_path = dst_path / original_filename
            print(f"DEBUG: dst является директорией, ищем файл: {copied_file_path}")

            if copied_file_path.exists():
                print(f"DEBUG: Удаляем скопированный файл: {copied_file_path}")
                copied_file_path.unlink()
                return True
            else:
                print(f"DEBUG: Скопированный файл не найден: {copied_file_path}")
                return False
        else:
            # Если dst является файлом, просто удаляем его
            print(f"DEBUG: Удаляем файл: {dst_path}")
            dst_path.unlink()
            return True

    except Exception as e:
        logging.error(f"Ошибка при отмене cp: {e}")
        print(f"DEBUG: Ошибка отмены cp: {e}")
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
        return False


def undo_rm(undo_data: dict) -> bool:
    """Отменяет команду rm - восстанавливает файл из корзины"""
    try:
        original_path = undo_data.get("path")
        trash_path = undo_data.get("trash_path")

        print(f"DEBUG undo_rm: original_path={original_path}")
        print(f"DEBUG undo_rm: trash_path={trash_path}")

        if not trash_path:
            print("DEBUG: Не указан путь к корзине в undo_data")
            return False

        if not original_path:
            print("DEBUG: Не указан исходный путь в undo_data")
            return False

        trash_file = Path(trash_path)
        original_file = Path(original_path)

        # Проверяем существование файла в корзине
        if not trash_file.exists():
            print(f"DEBUG: Файл в корзине не существует: {trash_path}")
            print(f"DEBUG: Абсолютный путь корзины: {trash_file.absolute()}")

            # Покажем содержимое корзины для отладки
            trash_dir = Path(TRASH_DIR).absolute()
            print(f"DEBUG: Содержимое корзины ({trash_dir}):")
            if trash_dir.exists():
                for item in trash_dir.iterdir():
                    print(f"DEBUG:   - {item.name}")
            else:
                print(f"DEBUG: Корзина не существует: {trash_dir}")

            # Попробуем найти файл в корзине по имени
            original_name = original_file.name
            print(f"DEBUG: Ищем файл по имени: {original_name}")
            if trash_dir.exists():
                matching_files = list(trash_dir.glob(f"*{original_name}"))
                print(f"DEBUG: Найдено файлов: {matching_files}")
                if matching_files:
                    trash_file = matching_files[0]
                    print(f"DEBUG: Используем альтернативный путь: {trash_file}")
                else:
                    print(f"DEBUG: Файл с именем *{original_name} не найден в корзине")
                    return False
            else:
                print("DEBUG: Корзина не существует")
                return False

        print(f"DEBUG: Файл в корзине найден: {trash_file}")
        print(f"DEBUG: Восстанавливаем в: {original_file}")

        # Создаем родительские директории если нужно
        original_file.parent.mkdir(parents=True, exist_ok=True)

        print(f"DEBUG: Перемещаем {trash_file} -> {original_file}")

        # Восстанавливаем файл
        shutil.move(str(trash_file), str(original_file))

        # Проверяем успешность восстановления
        if original_file.exists():
            print(f"DEBUG: Файл успешно восстановлен: {original_file}")
            return True
        else:
            print(f"DEBUG: Файл не был восстановлен: {original_file}")
            return False

    except Exception as e:
        logging.error(f"Ошибка при отмене rm: {e}")
        print(f"DEBUG: Ошибка отмены rm: {e}")
        return False


def cp_with_history(src: str, dst: str) -> None:
    """Копирование с записью в историю"""
    try:
        src_path = Path(src)
        dst_path = Path(dst)

        print(f"DEBUG: cp_with_history - src: {src_path}, dst: {dst_path}")

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

        print(f"DEBUG: Сохраняем в историю: {undo_data}")
        add_to_history("cp", [src, dst], undo_data)

    except Exception as e:
        logging.error(f"Ошибка при копировании: {e}")
        raise


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
        raise


def rm_with_history(path: str) -> None:
    """Удаление с перемещением в корзину и записью в историю"""
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            raise FileNotFoundError(f"Файл или директория не существует: {path}")

        # Получаем абсолютные пути
        absolute_path = path_obj.absolute()

        # Убедимся, что корзина существует
        trash_dir = Path(TRASH_DIR).absolute()
        trash_dir.mkdir(exist_ok=True)

        # Создаем уникальное имя в корзине
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        trash_name = f"{timestamp}_{path_obj.name}"
        trash_path = trash_dir / trash_name

        print(f"DEBUG rm_with_history: перемещаем {absolute_path} -> {trash_path}")

        # Перемещаем в корзину
        shutil.move(str(absolute_path), str(trash_path))

        # Проверяем, что файл действительно переместился
        if not trash_path.exists():
            raise Exception(f"Файл не был перемещен в корзину: {trash_path}")

        if absolute_path.exists():
            raise Exception(f"Исходный файл все еще существует: {absolute_path}")

        # Добавляем в историю с данными для отмены
        undo_data = {
            "path": str(absolute_path),
            "trash_path": str(trash_path)
        }

        print(f"DEBUG rm_with_history: записываем в историю: {undo_data}")

        from src.sub_functions.history_dependences import add_to_history
        add_to_history("rm", [path], undo_data)

        print(f"DEBUG: Файл успешно перемещен в корзину и запись добавлена в историю")

    except Exception as e:
        logging.error(f"Ошибка при удалении {path}: {e}")
        print(f"DEBUG: Ошибка при удалении: {e}")
        raise