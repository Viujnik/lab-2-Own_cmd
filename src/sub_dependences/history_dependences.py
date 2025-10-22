import logging
from pathlib import Path
from datetime import datetime

# Константы
HISTORY_FILE = ".history"
MAX_HISTORY_SIZE = 100


def history_mkdir() -> None:
    """Инициализирует файл истории"""
    try:
        history_file = Path(HISTORY_FILE)
        if not history_file.exists():
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                f.write("")
    except Exception as e:
        logging.error(f"Ошибка инициализации истории: {e}")
        raise e


def add_to_history(command: str, args: list, undo_data: dict = None) -> None:
    """Добавляет команду в историю"""
    try:
        # Форматируем запись
        timestamp = datetime.now().isoformat()
        args_str = " ".join(args)

        if undo_data:
            # Собираем undo_data в формат: key1=value1|key2=value2
            undo_parts = []
            for key, value in undo_data.items():
                # Заменяем разделители в значениях, чтобы не ломать парсинг
                safe_value = str(value).replace('|', '%%PIPE%%').replace('=', '%%EQUALS%%')
                undo_parts.append(f"{key}={safe_value}")
            undo_str = "|".join(undo_parts)
            record = f"{timestamp}|{command}|{args_str}|{undo_str}\n"
        else:
            record = f"{timestamp}|{command}|{args_str}|\n"


        # Добавляем в конец файла
        with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
            f.write(record)

        # Периодически чистим историю
        clean_history_if_needed()

    except Exception as e:
        logging.error(f"Ошибка при добавлении в историю: {e}")
        raise e


def clean_history_if_needed() -> None:
    """Очищает историю если она превысила максимальный размер"""
    try:
        if not Path(HISTORY_FILE).exists():
            return

        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if len(lines) > MAX_HISTORY_SIZE:
            lines_to_keep = lines[-MAX_HISTORY_SIZE:]

            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                f.writelines(lines_to_keep)

    except Exception as e:
        logging.error(f"Ошибка при очистке истории: {e}")
        raise e


def read_history() -> list:
    """Читает историю команд"""
    history = []
    try:
        if not Path(HISTORY_FILE).exists():
            return history

        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                parts = line.split('|')
                if len(parts) >= 3:
                    record = {
                        "id": line_num,
                        "timestamp": parts[0],
                        "command": parts[1],
                        "args": parts[2].split() if parts[2] else [],
                        "undo_data": {}
                    }

                    # Парсим undo_data если она есть
                    if len(parts) > 3:
                        for i in range(3, len(parts)):
                            item = parts[i]
                            if '=' in item:
                                key, value = item.split('=', 1)
                                # Восстанавливаем специальные символы в значениях
                                value = value.replace('%%PIPE%%', '|').replace('%%EQUALS%%', '=')
                                record["undo_data"][key] = value

                    history.append(record)

    except Exception as e:
        logging.error(f"Ошибка при чтении истории: {e}")
        raise e

    return history


def save_history(history: list) -> None:
    """Сохраняет историю команд"""
    try:
        lines = []
        for record in history:
            timestamp = record["timestamp"]
            command = record["command"]
            args_str = " ".join(record["args"])

            undo_data = record.get("undo_data", {})
            if undo_data:
                undo_str = "|".join(f"{k}={v}" for k, v in undo_data.items())
                line = f"{timestamp}|{command}|{args_str}|{undo_str}\n"
            else:
                line = f"{timestamp}|{command}|{args_str}|\n"

            lines.append(line)

        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            f.writelines(lines)

    except Exception as e:
        logging.error(f"Ошибка при сохранении истории: {e}")
        raise e


def history_args_parse(args: list[str]) -> dict[str, int]:
    """Парсит аргументы команды history"""
    args_value = {
        "count": 10,
        "clear": 0
    }

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "-c":
            args_value["clear"] = True
        elif arg.isdigit():
            args_value["count"] = int(arg)
        elif arg.startswith('-'):
            error_msg = f"history: неверная опция '{arg}'"
            logging.error(error_msg)
            raise ValueError(error_msg)
        i += 1

    return args_value


def history_realisation(args: dict[str, int]) -> None:
    """Основная реализация функции history"""
    try:
        count = args["count"]
        clear = bool(args["clear"])

        if clear:
            Path(HISTORY_FILE).write_text("", encoding='utf-8')

        history = read_history()

        recent_commands = history[-count:] if count < len(history) else history
        for record in recent_commands:
            cmd_id = record["id"]
            timestamp = datetime.fromisoformat(record["timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
            command = record["command"]
            cmd_args = " ".join(record["args"])
            print(f"{cmd_id:4} {timestamp}  {command} {cmd_args}")

    except Exception as e:
        error_msg = f"Ошибка при выводе истории: {e}"
        logging.error(error_msg)
        raise e
