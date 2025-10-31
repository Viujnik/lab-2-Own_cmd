import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.sub_functions.cp_dependences import cp_args_parse
from src.sub_functions.mv_dependences import mv_args_parse, filesystem_check
from src.sub_functions.rm_dependences import rm_args_parse
from src.sub_functions.undo_dependences import (
    cp_with_history, mv_with_history, rm_with_history,
    undo_args_parse, undo_realisation, undo_rm, undo_cp, undo_mv, undo_command
)

# Добавляем корневую директорию проекта в Python path для корректного импорта
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

"""
Тесты файловых операций: cp, mv, rm и их отмена через undo (только мок-тесты)
"""


class TestFileOperationsWithMocks(unittest.TestCase):
    """Тесты для файловых операций с использованием моков"""

    @patch('src.sub_functions.cp_dependences.Path')
    def test_cp_args_parse_valid(self, mock_path):
        """Тест парсинга аргументов cp с валидными путями"""
        # Используем подход из config_tests.py
        mock_src = MagicMock()
        mock_src.exists.return_value = True
        mock_src.__str__ = MagicMock(return_value='source.txt')

        mock_dst = MagicMock()
        mock_dst.exists.return_value = True
        mock_dst.__str__ = MagicMock(return_value='dest_dir')

        mock_path.side_effect = [mock_src, mock_dst]

        result = cp_args_parse(['source.txt', 'dest_dir'])
        self.assertEqual(result, ['source.txt', 'dest_dir'])

    @patch('src.sub_functions.cp_dependences.Path')
    def test_cp_args_parse_nonexistent_source(self, mock_path):
        """Тест парсинга аргументов cp с несуществующим исходным файлом"""
        mock_src = MagicMock()
        mock_src.exists.return_value = False
        mock_path.return_value = mock_src

        with self.assertRaises(FileNotFoundError):
            cp_args_parse(['/nonexistent/file', 'dest_dir'])

    @patch('src.sub_functions.cp_dependences.Path')
    def test_cp_args_parse_nonexistent_destination(self, mock_path):
        """Тест парсинга аргументов cp с несуществующей директорией назначения"""
        mock_src = MagicMock()
        mock_src.exists.return_value = True

        mock_dst = MagicMock()
        mock_dst.exists.return_value = False

        mock_path.side_effect = [mock_src, mock_dst]

        with self.assertRaises(NotADirectoryError):
            cp_args_parse(['source.txt', '/nonexistent/dir'])

    def test_cp_args_parse_insufficient_args(self):
        """Тест парсинга аргументов cp с недостаточным количеством аргументов"""
        with self.assertRaises(Exception) as context:
            cp_args_parse(['source.txt'])
        self.assertIn("Введите 2 аргумента", str(context.exception))

    @patch('os.path.isdir')
    @patch('os.path.exists')
    def test_mv_args_parse_valid(self, mock_exists, mock_isdir):
        """Тест парсинга аргументов mv с валидными путями"""
        mock_exists.side_effect = [True, True]  # Оба пути существуют
        mock_isdir.return_value = True  # Второй путь - директория

        result = mv_args_parse(['source.txt', 'dest_dir'])
        self.assertEqual(result, ['source.txt', 'dest_dir'])

    @patch('os.path.isdir')
    @patch('os.path.exists')
    def test_mv_args_parse_nonexistent_source(self, mock_exists, mock_isdir):
        """Тест парсинга аргументов mv с несуществующим исходным файлом"""
        mock_exists.side_effect = [False, True]  # Исходный файл не существует
        mock_isdir.return_value = True  # Второй путь - директория

        with self.assertRaises(Exception) as context:
            mv_args_parse(['/nonexistent/file', 'dest_dir'])
        self.assertIn("Файла /nonexistent/file не существует", str(context.exception))

    @patch('os.path.exists')
    @patch('os.path.isdir')
    def test_mv_args_parse_not_directory(self, mock_isdir, mock_exists):
        """Тест парсинга аргументов mv когда назначение не директория"""
        mock_exists.return_value = True
        mock_isdir.return_value = False  # Назначение не директория

        with self.assertRaises(Exception) as context:
            mv_args_parse(['source.txt', 'not_a_dir'])
        self.assertIn("не является директорией", str(context.exception))

    def test_mv_args_parse_insufficient_args(self):
        """Тест парсинга аргументов mv с недостаточным количеством аргументов"""
        with self.assertRaises(Exception) as context:
            mv_args_parse(['source.txt'])
        self.assertIn("2 аргумента", str(context.exception))

    @patch('os.stat')
    def test_filesystem_check_same_device(self, mock_stat):
        """Тест проверки файловой системы - файлы на одном устройстве"""
        mock_stat1 = MagicMock()
        mock_stat1.st_dev = 1

        mock_stat2 = MagicMock()
        mock_stat2.st_dev = 1

        mock_stat.side_effect = [mock_stat1, mock_stat2]

        result = filesystem_check('/path1', '/path2')
        self.assertTrue(result)

    @patch('os.stat')
    def test_filesystem_check_different_devices(self, mock_stat):
        """Тест проверки файловой системы - файлы на разных устройствах"""
        mock_stat1 = MagicMock()
        mock_stat1.st_dev = 1

        mock_stat2 = MagicMock()
        mock_stat2.st_dev = 2

        mock_stat.side_effect = [mock_stat1, mock_stat2]

        result = filesystem_check('/path1', '/path2')
        self.assertFalse(result)

    @patch('os.stat')
    def test_filesystem_check_os_error(self, mock_stat):
        """Тест проверки файловой системы с ошибкой OS"""
        mock_stat.side_effect = OSError("Permission denied")

        result = filesystem_check('/path1', '/path2')
        self.assertFalse(result)

    @patch('src.sub_functions.rm_dependences.os.path.normpath')
    def test_rm_args_parse_valid_without_flag(self, mock_normpath):
        """Тест парсинга аргументов rm без флага -r"""
        mock_normpath.return_value = '/test/path'

        result = rm_args_parse(['/test/path'])
        self.assertEqual(result, {
            "r_flag": False,
            "path": '/test/path'
        })

    @patch('src.sub_functions.rm_dependences.os.path.normpath')
    def test_rm_args_parse_valid_with_flag(self, mock_normpath):
        """Тест парсинга аргументов rm с флагом -r"""
        mock_normpath.return_value = '/test/path'

        result = rm_args_parse(['-r', '/test/path'])
        self.assertEqual(result, {
            "r_flag": True,
            "path": '/test/path'
        })

    @patch('src.sub_functions.rm_dependences.os.path.normpath')
    def test_rm_args_parse_mixed_order(self, mock_normpath):
        """Тест парсинга аргументов rm со смешанным порядком"""
        mock_normpath.return_value = '/test/path'

        result = rm_args_parse(['/test/path', '-r'])
        self.assertEqual(result, {
            "r_flag": True,
            "path": '/test/path'
        })

    def test_rm_args_parse_no_path(self):
        """Тест парсинга аргументов rm без пути"""
        with self.assertRaises(Exception) as context:
            rm_args_parse(['-r'])
        self.assertIn("Пустой аргумент пути/файла", str(context.exception))

    @patch('src.sub_functions.undo_dependences.add_to_history')
    @patch('src.sub_functions.undo_dependences.shutil.copy2')
    @patch('src.sub_functions.undo_dependences.Path')
    def test_cp_with_history_file_to_dir(self, mock_path, mock_copy2, mock_add_history):
        """Тест копирования файла в директорию с записью в историю"""
        # Настраиваем моки с правильными путями
        mock_src_path = MagicMock()
        mock_src_path.is_file.return_value = True
        mock_src_path.absolute.return_value = Path("/absolute/source.txt")
        mock_src_path.name = "source.txt"

        mock_dst_path = MagicMock()
        mock_dst_path.is_dir.return_value = True
        mock_dst_path.absolute.return_value = Path("/absolute/dest_dir")

        mock_final_path = MagicMock()
        mock_final_path.__str__ = MagicMock(return_value="/absolute/dest_dir/source.txt")

        mock_dst_path.__truediv__.return_value = mock_final_path

        mock_path.side_effect = [mock_src_path, mock_dst_path]

        cp_with_history("source.txt", "dest_dir")

        # Проверяем вызовы
        mock_copy2.assert_called_once_with("source.txt", mock_final_path)
        mock_add_history.assert_called_once()

    @patch('src.sub_functions.undo_dependences.add_to_history')
    @patch('src.sub_functions.undo_dependences.shutil.copy2')
    @patch('src.sub_functions.undo_dependences.Path')
    def test_cp_with_history_file_to_file(self, mock_path, mock_copy2, mock_add_history):
        """Тест копирования файла в файл с записью в историю"""
        # Настраиваем моки
        mock_src_path = MagicMock()
        mock_src_path.is_file.return_value = True
        mock_src_path.absolute.return_value = Path("/absolute/source.txt")

        mock_dst_path = MagicMock()
        mock_dst_path.is_dir.return_value = False
        mock_dst_path.absolute.return_value = Path("/absolute/dest.txt")

        mock_path.side_effect = [mock_src_path, mock_dst_path]

        cp_with_history("source.txt", "dest.txt")

        # Проверяем вызовы
        mock_copy2.assert_called_once_with("source.txt", "dest.txt")
        mock_add_history.assert_called_once()

    @patch('src.sub_functions.undo_dependences.shutil.copy2')
    @patch('src.sub_functions.undo_dependences.Path')
    def test_cp_with_history_permission_error(self, mock_path, mock_copy2):
        """Тест копирования с ошибкой прав доступа"""
        # Настраиваем моки
        mock_src_path = MagicMock()
        mock_src_path.is_file.return_value = True
        mock_src_path.absolute.return_value = Path("/absolute/source.txt")

        mock_dst_path = MagicMock()
        mock_dst_path.is_dir.return_value = True
        mock_dst_path.absolute.return_value = Path("/absolute/dest_dir")

        mock_path.side_effect = [mock_src_path, mock_dst_path]

        mock_copy2.side_effect = PermissionError("Permission denied")

        with self.assertRaises(PermissionError):
            cp_with_history("source.txt", "dest_dir")

    @patch('src.sub_functions.undo_dependences.add_to_history')
    @patch('src.sub_functions.undo_dependences.shutil.move')
    @patch('src.sub_functions.undo_dependences.Path')
    @patch('builtins.input')
    def test_rm_with_history_file_confirmed(self, mock_input, mock_path, mock_move, mock_add_history):
        """Тест удаления файла с подтверждением и записью в историю"""
        # Настраиваем моки
        mock_input.return_value = 'y'  # Пользователь подтверждает удаление

        mock_path_obj = MagicMock()
        mock_path_obj.exists.return_value = True
        mock_path_obj.absolute.return_value = Path("/absolute/test.txt")
        mock_path_obj.name = "test.txt"

        # Мокаем корзину
        with patch('src.sub_functions.undo_dependences.TRASH_DIR', '/absolute/.trash'):
            with patch('src.sub_functions.undo_dependences.Path') as mock_trash_path:
                mock_trash_dir = MagicMock()
                mock_trash_dir.mkdir.return_value = None
                mock_trash_path.return_value = mock_trash_dir

                rm_with_history("test.txt")

        # Проверяем вызовы
        mock_move.assert_called_once()
        mock_add_history.assert_called_once()

    @patch('src.sub_functions.undo_dependences.Path')
    @patch('builtins.input')
    def test_rm_with_history_cancelled(self, mock_input, mock_path):
        """Тест отмены удаления файла"""
        # Настраиваем моки
        mock_input.return_value = 'n'  # Пользователь отменяет удаление

        mock_path_obj = MagicMock()
        mock_path_obj.exists.return_value = True
        mock_path.return_value = mock_path_obj

        rm_with_history("test.txt")

        # Проверяем, что удаление не произошло
        mock_input.assert_called_once()
        # Другие функции не должны вызываться

    @patch('src.sub_functions.undo_dependences.Path')
    def test_rm_with_history_nonexistent_file(self, mock_path):
        """Тест удаления несуществующего файла"""
        mock_path_obj = MagicMock()
        mock_path_obj.exists.return_value = False
        mock_path.return_value = mock_path_obj

        with self.assertRaises(FileNotFoundError):
            rm_with_history("/nonexistent/file")

    @patch('src.sub_functions.undo_dependences.add_to_history')
    @patch('src.sub_functions.undo_dependences.shutil.move')
    @patch('src.sub_functions.undo_dependences.Path')
    def test_mv_with_history_file(self, mock_path, mock_move, mock_add_history):
        """Тест перемещения файла с записью в историю"""
        # Настраиваем моки со строковым представлением
        mock_src_path = MagicMock()
        mock_src_path.absolute.return_value = Path("/absolute/source.txt")
        mock_src_path.__str__ = MagicMock(return_value="source.txt")

        mock_dst_path = MagicMock()
        mock_dst_path.absolute.return_value = Path("/absolute/dest.txt")
        mock_dst_path.__str__ = MagicMock(return_value="dest.txt")

        mock_path.side_effect = [mock_src_path, mock_dst_path]

        mv_with_history("source.txt", "dest.txt")

        # Проверяем вызовы
        mock_move.assert_called_once_with("source.txt", "dest.txt")  # Теперь работает!
        mock_add_history.assert_called_once()

    def test_undo_args_parse_default(self):
        """Тест парсинга аргументов undo по умолчанию"""
        result = undo_args_parse([])
        self.assertEqual(result, {"steps": 1})

    def test_undo_args_parse_with_steps(self):
        """Тест парсинга аргументов undo с указанием количества шагов"""
        result = undo_args_parse(["3"])
        self.assertEqual(result, {"steps": 3})

    def test_undo_args_parse_invalid_option(self):
        """Тест парсинга аргументов undo с неверной опцией"""
        with self.assertRaises(ValueError) as context:
            undo_args_parse(["-x"])
        self.assertIn("неверная опция", str(context.exception))

    @patch('src.sub_functions.undo_dependences.read_history')
    def test_undo_realisation_no_history(self, mock_read):
        """Тест отмены при пустой истории"""
        mock_read.return_value = []
        with self.assertRaises(Exception) as context:
            undo_realisation({"steps": 1})
        self.assertIn("История команд пуста", str(context.exception))

    @patch('src.sub_functions.undo_dependences.read_history')
    @patch('src.sub_functions.undo_dependences.save_history')
    @patch('src.sub_functions.undo_dependences.undo_command')
    def test_undo_realisation_success(self, mock_undo_command, mock_save_history, mock_read_history):
        """Тест успешной отмены команд"""
        # Мокаем историю с командами для отмены
        mock_history = [
            {"command": "cp", "undo_data": {"src": "/src", "dst": "/dst"}},
            {"command": "rm", "undo_data": {"path": "/path", "trash_path": "/trash"}}
        ]
        mock_read_history.return_value = mock_history
        mock_undo_command.return_value = True

        undo_realisation({"steps": 2})

        self.assertEqual(mock_undo_command.call_count, 2)
        mock_save_history.assert_called_once()

    @patch('src.sub_functions.undo_dependences.read_history')
    def test_undo_realisation_no_undoable_commands(self, mock_read):
        """Тест отмены когда нет команд для отмены"""
        mock_read.return_value = [
            {"command": "ls", "args": ["-l"]},  # Не поддерживается для отмены
            {"command": "cat", "args": ["file.txt"]}  # Не поддерживается для отмены
        ]
        with self.assertRaises(Exception) as context:
            undo_realisation({"steps": 1})
        self.assertIn("Нет команд для отмены", str(context.exception))

    @patch('src.sub_functions.undo_dependences.undo_cp')
    def test_undo_command_cp(self, mock_undo_cp):
        """Тест отмены команды cp"""
        mock_undo_cp.return_value = True
        record = {"command": "cp", "undo_data": {"src": "/src", "dst": "/dst"}}

        result = undo_command(record)

        self.assertTrue(result)
        mock_undo_cp.assert_called_once_with({"src": "/src", "dst": "/dst"})

    @patch('src.sub_functions.undo_dependences.undo_mv')
    def test_undo_command_mv(self, mock_undo_mv):
        """Тест отмены команды mv"""
        mock_undo_mv.return_value = True
        record = {"command": "mv", "undo_data": {"src": "/src", "dst": "/dst"}}

        result = undo_command(record)

        self.assertTrue(result)
        mock_undo_mv.assert_called_once_with({"src": "/src", "dst": "/dst"})

    @patch('src.sub_functions.undo_dependences.undo_rm')
    def test_undo_command_rm(self, mock_undo_rm):
        """Тест отмены команды rm"""
        mock_undo_rm.return_value = True
        record = {"command": "rm", "undo_data": {"path": "/path", "trash_path": "/trash"}}

        result = undo_command(record)

        self.assertTrue(result)
        mock_undo_rm.assert_called_once_with({"path": "/path", "trash_path": "/trash"})

    def test_undo_command_unknown(self):
        """Тест отмены неизвестной команды"""
        record = {"command": "unknown", "undo_data": {}}

        result = undo_command(record)

        self.assertFalse(result)


class TestUndoFunctionsWithMocks(unittest.TestCase):
    """Тесты для функций отмены с использованием моков"""

    @patch('src.sub_functions.undo_dependences.Path')
    def test_undo_cp_file_to_file(self, mock_path):
        """Тест отмены копирования файла в файл"""
        # Настраиваем моки
        mock_dst_path = MagicMock()
        mock_dst_path.exists.return_value = True
        mock_dst_path.is_dir.return_value = False

        mock_path.return_value = mock_dst_path

        undo_data = {"src": "/src", "dst": "/dst"}
        result = undo_cp(undo_data)

        self.assertTrue(result)
        mock_dst_path.unlink.assert_called_once()

    @patch('src.sub_functions.undo_dependences.Path')
    def test_undo_cp_file_to_dir(self, mock_path):
        """Тест отмены копирования файла в директорию"""
        # Настраиваем моки
        mock_dst_path = MagicMock()
        mock_dst_path.exists.return_value = True
        mock_dst_path.is_dir.return_value = True

        mock_copied_file = MagicMock()
        mock_copied_file.exists.return_value = True

        mock_dst_path.__truediv__.return_value = mock_copied_file

        mock_path.return_value = mock_dst_path

        undo_data = {"src": "/src/file.txt", "dst": "/dst_dir"}
        result = undo_cp(undo_data)

        self.assertTrue(result)
        mock_copied_file.unlink.assert_called_once()

    @patch('src.sub_functions.undo_dependences.Path')
    def test_undo_cp_nonexistent_destination(self, mock_path):
        """Тест отмены копирования когда файл назначения не существует"""
        mock_dst_path = MagicMock()
        mock_dst_path.exists.return_value = False
        mock_path.return_value = mock_dst_path

        undo_data = {"src": "/src", "dst": "/nonexistent"}
        result = undo_cp(undo_data)

        self.assertFalse(result)

    @patch('src.sub_functions.undo_dependences.shutil.move')
    @patch('src.sub_functions.undo_dependences.Path')
    @patch('builtins.input')  # Добавляем мок для input
    def test_undo_mv(self, mock_input, mock_path, mock_move):
        """Тест отмены перемещения файла"""
        # Настраиваем моки
        mock_input.return_value = 'y'  # Подтверждение перезаписи

        mock_dst_path = MagicMock()
        mock_dst_path.exists.return_value = True
        mock_dst_path.__str__ = MagicMock(return_value="/dst")

        mock_src_path = MagicMock()
        mock_src_path.__str__ = MagicMock(return_value="/src")
        mock_src_path.parent.exists.return_value = True
        mock_src_path.exists.return_value = True

        def path_side_effect(path):
            if path == "/dst":
                return mock_dst_path
            elif path == "/src":
                return mock_src_path
            else:
                return MagicMock()

        mock_path.side_effect = path_side_effect

        # Настраиваем side_effect для shutil.move, чтобы изменить состояние файлов
        def move_side_effect(src, dst):
            mock_dst_path.exists.return_value = False
            mock_src_path.exists.return_value = True

        mock_move.side_effect = move_side_effect

        undo_data = {"src": "/src", "dst": "/dst"}
        result = undo_mv(undo_data)

        self.assertTrue(result)
        mock_move.assert_called_once_with("/dst", "/src")
        mock_input.assert_called_once()

    @patch('src.sub_functions.undo_dependences.Path')
    def test_undo_mv_nonexistent_destination(self, mock_path):
        """Тест отмены перемещения когда файл назначения не существует"""
        mock_dst_path = MagicMock()
        mock_dst_path.exists.return_value = False
        mock_path.return_value = mock_dst_path

        undo_data = {"src": "/src", "dst": "/nonexistent"}
        result = undo_mv(undo_data)

        self.assertFalse(result)

    @patch('src.sub_functions.undo_dependences.shutil.move')
    @patch('src.sub_functions.undo_dependences.Path')
    def test_undo_rm(self, mock_path, mock_move):
        """Тест отмены удаления файла"""
        # Настраиваем моки с правильными строковыми представлениями
        mock_trash_path = MagicMock()
        mock_trash_path.exists.return_value = True
        mock_trash_path.__str__ = MagicMock(return_value="/trash")

        mock_original_path = MagicMock()
        mock_original_path.parent.mkdir.return_value = None
        mock_original_path.__str__ = MagicMock(return_value="/original")

        mock_path.side_effect = [mock_trash_path, mock_original_path]

        undo_data = {
            "path": "/original",
            "trash_path": "/trash"
        }
        result = undo_rm(undo_data)

        self.assertTrue(result)
        mock_move.assert_called_once_with("/trash", "/original")

    @patch('src.sub_functions.undo_dependences.shutil.move')
    @patch('src.sub_functions.undo_dependences.Path')
    def test_undo_rm_nonexistent_trash_file(self, mock_path, mock_move):
        """Тест отмены удаления когда файл в корзине не существует"""
        # Настраиваем моки
        mock_trash_path = MagicMock()
        mock_trash_path.exists.return_value = False

        mock_original_path = MagicMock()
        mock_original_path.parent.mkdir.return_value = None

        # Настраиваем side_effect для правильного распределения моков
        def path_side_effect(path):
            if path == "/nonexistent/trash":
                return mock_trash_path
            elif path == "/path":
                return mock_original_path
            else:
                return MagicMock()

        mock_path.side_effect = path_side_effect

        # Мокаем shutil.move чтобы выбросить исключение
        mock_move.side_effect = FileNotFoundError("File not found")

        undo_data = {
            "path": "/path",
            "trash_path": "/nonexistent/trash"
        }

        # Ожидаем, что функция выбросит исключение
        with self.assertRaises(FileNotFoundError):
            undo_rm(undo_data)


if __name__ == '__main__':
    unittest.main()
