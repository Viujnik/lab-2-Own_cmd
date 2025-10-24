# clear_dependences.py
import os
import sys


def clear_realisation():
    """
    Улучшенная очистка экрана с определением типа окружения
    """
    try:
        # Проверяем тип окружения
        env_type = get_environment_type()

        if env_type == "terminal":
            # В терминале используем системные команды
            if os.name == 'nt':
                os.system('cls')
            else:
                os.system('clear')
        else:
            # В IDE используем резервные методы
            clear_for_ide()

    except Exception as e:
        raise e


def get_environment_type():
    """Определяет тип окружения (терминал или IDE)"""
    # Проверяем переменные окружения IDE
    ide_indicators = ['PYCHARM_HOSTED', 'VSCODE_PID', 'JETBRAINS_IDE', 'SPYDER']

    for indicator in ide_indicators:
        if indicator in os.environ:
            return "ide"

    # Проверяем, является ли stdout терминалом
    if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
        return "terminal"

    return "unknown"


def clear_for_ide():
    """Очистка экрана для IDE"""
    # ANSI escape codes
    print("\033[2J\033[H", end="")
    # Пустые строки (меньше для IDE)
    print("\n" * 50)
