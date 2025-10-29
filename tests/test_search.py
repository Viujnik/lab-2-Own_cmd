import os
import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open, call
from src.sub_functions.cat_dependences import cat_args_parse, cat_realisation
from src.sub_functions.grep_dependences import grep_args_parse, grep_realisation
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

"""
Тесты команд поиска и работы с содержимым файлов: cat и grep
"""

class TestCatCommands(unittest.TestCase):
    """Тесты для команды cat"""
    def test_cat_args_parse_no_args(self):
        """Тест cat_args_parse без аргументов - должен выбросить исключение"""
        with self.assertRaises(Exception) as context:
            cat_args_parse([])
        self.assertEqual(str(context.exception), "Для команды cat ожидается 2-ой аргумент - файл или путь к файлу")

    def test_cat_args_parse_empty_string_arg(self):
        """Тест cat_args_parse с пустой строкой - должен выбросить исключение"""
        with self.assertRaises(Exception) as context:
            cat_args_parse([''])
        self.assertEqual(str(context.exception), "Для команды cat ожидается 2-ой аргумент - файл или путь к файлу")

    @patch('src.sub_functions.cat_dependences.Path')
    def test_cat_args_parse_directory_path(self, mock_path):
        """Тест cat_args_parse с путем к директории - должен выбросить исключение"""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_dir.return_value = True
        mock_path_instance.is_symlink.return_value = False
        mock_path.return_value = mock_path_instance

        with self.assertRaises(Exception) as context:
            cat_args_parse(['/some/directory'])
        self.assertEqual(str(context.exception), "Для команды cat нужно передать файл или путь к файлу")

    @patch('src.sub_functions.cat_dependences.Path')
    def test_cat_args_parse_symlink_path(self, mock_path):
        """Тест cat_args_parse с путем к симлинку - должен выбросить исключение"""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_dir.return_value = False
        mock_path_instance.is_symlink.return_value = True
        mock_path.return_value = mock_path_instance

        with self.assertRaises(Exception) as context:
            cat_args_parse(['/some/symlink'])
        self.assertEqual(str(context.exception), "Для команды cat нужно передать файл или путь к файлу")

    @patch('src.sub_functions.cat_dependences.Path')
    def test_cat_args_parse_nonexistent_path(self, mock_path):
        """Тест cat_args_parse с несуществующим путем - должен выбросить FileNotFoundError"""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance

        with self.assertRaises(FileNotFoundError):
            cat_args_parse(['/nonexistent/file'])

    @patch('src.sub_functions.cat_dependences.Path')
    def test_cat_args_parse_valid_file(self, mock_path):
        """Тест cat_args_parse с валидным файлом - должен вернуть Path"""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_dir.return_value = False
        mock_path_instance.is_symlink.return_value = False
        mock_path.return_value = mock_path_instance

        result = cat_args_parse(['/valid/file.txt'])
        self.assertEqual(result, mock_path_instance)

    # ТЕСТЫ ДЛЯ cat_realisation
    @patch('src.sub_functions.cat_dependences.print')
    @patch('src.sub_functions.cat_dependences.Path')
    def test_cat_realisation_success(self, mock_path, mock_print):
        """Тест cat_realisation с валидным файлом - успешный случай"""
        mock_file_path = MagicMock()
        mock_path.return_value = mock_file_path

        mock_file_content = "Hello, World!\nThis is a test file."
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = mock_file_content
        mock_file_path.open.return_value = mock_file

        cat_realisation('/valid/file.txt')

        mock_path.assert_called_once_with('/valid/file.txt')
        mock_file_path.open.assert_called_once_with("r", encoding='utf-8')
        mock_print.assert_called_once_with(mock_file_content)

    @patch('src.sub_functions.cat_dependences.Path')
    def test_cat_realisation_file_not_found(self, mock_path):
        """Тест cat_realisation с несуществующим файлом - должен выбросить FileNotFoundError"""
        mock_file_path = MagicMock()
        mock_path.return_value = mock_file_path
        mock_file_path.open.side_effect = FileNotFoundError("File not found")

        with self.assertRaises(FileNotFoundError):
            cat_realisation('/nonexistent/file.txt')

    @patch('src.sub_functions.cat_dependences.Path')
    def test_cat_realisation_permission_error(self, mock_path):
        """Тест cat_realisation с файлом без прав доступа - должен выбросить PermissionError"""
        mock_file_path = MagicMock()
        mock_path.return_value = mock_file_path
        mock_file_path.open.side_effect = PermissionError("Permission denied")

        with self.assertRaises(PermissionError):
            cat_realisation('/restricted/file.txt')

    @patch('src.sub_functions.cat_dependences.Path')
    def test_cat_realisation_unicode_error(self, mock_path):
        """Тест cat_realisation с файлом в неправильной кодировке - должен выбросить UnicodeError"""
        mock_file_path = MagicMock()
        mock_path.return_value = mock_file_path
        mock_file_path.open.side_effect = UnicodeDecodeError('utf-8', b'\x00', 0, 1, 'invalid start byte')

        with self.assertRaises(UnicodeDecodeError):
            cat_realisation('/invalid/encoding/file.txt')

    @patch('src.sub_functions.cat_dependences.print')
    @patch('src.sub_functions.cat_dependences.Path')
    def test_cat_realisation_empty_file(self, mock_path, mock_print):
        """Тест cat_realisation с пустым файлом - успешный случай"""
        mock_file_path = MagicMock()
        mock_path.return_value = mock_file_path

        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = ""
        mock_file_path.open.return_value = mock_file

        cat_realisation('/empty/file.txt')

        mock_path.assert_called_once_with('/empty/file.txt')
        mock_file_path.open.assert_called_once_with("r", encoding='utf-8')
        mock_print.assert_called_once_with("")

    @patch('src.sub_functions.cat_dependences.print')
    @patch('src.sub_functions.cat_dependences.Path')
    def test_cat_realisation_large_file(self, mock_path, mock_print):
        """Тест cat_realisation с большим файлом - успешный случай"""
        mock_file_path = MagicMock()
        mock_path.return_value = mock_file_path

        large_content = "Line " + "x" * 1000 + "\n"
        large_content = large_content * 100

        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = large_content
        mock_file_path.open.return_value = mock_file

        cat_realisation('/large/file.txt')

        mock_path.assert_called_once_with('/large/file.txt')
        mock_file_path.open.assert_called_once_with("r", encoding='utf-8')
        mock_print.assert_called_once_with(large_content)


class TestGrepCommands(unittest.TestCase):
    """Тесты для команды поиска grep"""

    @staticmethod
    def _create_mock_file(name, is_file=True, is_dir=False):
        """Создает мок файла с заданными характеристиками"""
        mock_file = MagicMock()
        mock_file.is_file.return_value = is_file
        mock_file.is_dir.return_value = is_dir
        mock_file.__str__ = lambda self: name
        return mock_file

    def test_grep_args_parse_minimal_args(self):
        """Тест парсинга аргументов grep с минимальным набором"""
        result = grep_args_parse(['pattern', 'file.txt'])
        expected = {'options': '', 'pattern': 'pattern', 'path': 'file.txt'}
        self.assertEqual(result, expected)

    def test_grep_args_parse_with_options(self):
        """Тест парсинга аргументов grep с опциями"""
        result = grep_args_parse(['-r', '-i', 'pattern', 'folder'])
        expected = {'options': '-r -i ', 'pattern': 'pattern', 'path': 'folder'}
        self.assertEqual(result, expected)

    def test_grep_args_parse_mixed_order(self):
        """Тест парсинга аргументов grep со смешанным порядком"""
        result = grep_args_parse(['-i', 'pattern', '-r', 'folder'])
        expected = {'options': '-i -r ', 'pattern': 'pattern', 'path': 'folder'}
        self.assertEqual(result, expected)

    def test_grep_args_parse_insufficient_args(self):
        """Тест парсинга аргументов grep с недостаточным количеством аргументов"""
        with self.assertRaises(SyntaxError):
            grep_args_parse(['pattern'])

    def test_grep_args_parse_no_pattern(self):
        """Тест парсинга аргументов grep без шаблона"""
        with self.assertRaises(SyntaxError):
            grep_args_parse(['-r', 'folder'])

    @patch('src.sub_functions.grep_dependences.print')
    @patch('src.sub_functions.grep_dependences.Path')
    def test_grep_realisation_file_search_success(self, mock_path, mock_print):
        """Тест поиска в файле"""
        mock_file = self._create_mock_file('test.txt')
        mock_path.return_value = mock_file

        with patch('builtins.open', mock_open(read_data='line1\npattern line2\nline3\n')):
            grep_realisation({'options': '', 'pattern': 'pattern', 'path': 'test.txt'})
        mock_print.assert_called_once_with('test.txt:2:pattern line2')

    @patch('src.sub_functions.grep_dependences.print')
    @patch('src.sub_functions.grep_dependences.Path')
    def test_grep_realisation_case_insensitive(self, mock_path, mock_print):
        """Тест поиска без учета регистра"""
        mock_file = self._create_mock_file('test.txt')
        mock_path.return_value = mock_file

        with patch('builtins.open', mock_open(read_data='LINE1\nPATTERN line2\nline3\n')):
            grep_realisation({'options': '-i', 'pattern': 'pattern', 'path': 'test.txt'})
        mock_print.assert_called_once_with('test.txt:2:PATTERN line2')

    @patch('src.sub_functions.grep_dependences.print')
    @patch('src.sub_functions.grep_dependences.Path')
    def test_grep_realisation_multiple_matches(self, mock_path, mock_print):
        """Тест поиска с несколькими совпадениями"""
        mock_file = self._create_mock_file('test.txt')
        mock_path.return_value = mock_file

        with patch('builtins.open', mock_open(read_data='pattern1\nline2\npattern3\npattern4\n')):
            grep_realisation({'options': '', 'pattern': 'pattern', 'path': 'test.txt'})

        self.assertEqual(mock_print.call_count, 3)
        calls = [
            call('test.txt:1:pattern1'),
            call('test.txt:3:pattern3'),
            call('test.txt:4:pattern4')
        ]
        mock_print.assert_has_calls(calls, any_order=False)

    @patch('src.sub_functions.grep_dependences.Path')
    def test_grep_realisation_no_matches(self, mock_path):
        """Тест поиска без совпадений"""
        mock_file = self._create_mock_file('test.txt')
        mock_path.return_value = mock_file

        with patch('builtins.open', mock_open(read_data='line1\nline2\nline3\n')):
            grep_realisation({'options': '', 'pattern': 'pattern', 'path': 'test.txt'})

    @patch('src.sub_functions.grep_dependences.print')
    @patch('src.sub_functions.grep_dependences.Path')
    def test_grep_realisation_directory_non_recursive(self, mock_path, mock_print):
        """Тест поиска в директории без рекурсии"""
        mock_dir = self._create_mock_file('folder', is_file=False, is_dir=True)
        mock_path.return_value = mock_dir

        mock_file1 = self._create_mock_file('file1.txt')
        mock_file2 = self._create_mock_file('file2.txt')

        mock_dir.iterdir.return_value = [mock_file1, mock_file2]

        with patch('builtins.open') as mock_file_open:
            mock_file_open.side_effect = [
                mock_open(read_data='pattern found\n').return_value,
                mock_open(read_data='no match\n').return_value
            ]
            grep_realisation({'options': '', 'pattern': 'pattern', 'path': 'folder'})
        mock_print.assert_called_once_with('file1.txt:1:pattern found')

    @patch('src.sub_functions.grep_dependences.print')
    @patch('src.sub_functions.grep_dependences.Path')
    def test_grep_realisation_directory_recursive(self, mock_path, mock_print):
        """Тест поиска в директории с рекурсией"""
        mock_dir = self._create_mock_file('folder', is_file=False, is_dir=True)
        mock_path.return_value = mock_dir

        mock_file1 = self._create_mock_file('file1.txt')
        mock_subdir = self._create_mock_file('subfolder', is_file=False, is_dir=True)
        mock_file2 = self._create_mock_file('file2.txt')

        mock_dir.iterdir.return_value = [mock_file1, mock_subdir]
        mock_subdir.iterdir.return_value = [mock_file2]

        with patch('builtins.open') as mock_file_open:
            mock_file_open.side_effect = [
                mock_open(read_data='pattern1\n').return_value,
                mock_open(read_data='pattern2\n').return_value
            ]
            grep_realisation({'options': '-r', 'pattern': 'pattern', 'path': 'folder'})
        self.assertEqual(mock_print.call_count, 2)

    def test_grep_realisation_invalid_pattern(self):
        """Тест с невалидным регулярным выражением"""
        with self.assertRaises(ValueError):
            grep_realisation({'options': '', 'pattern': '[invalid', 'path': 'file.txt'})

    @patch('src.sub_functions.grep_dependences.Path')
    def test_grep_realisation_file_not_found(self, mock_path):
        """Тест с несуществующим путем"""
        mock_path_obj = self._create_mock_file('nonexistent', is_file=False, is_dir=False)
        mock_path.return_value = mock_path_obj

        with self.assertRaises(FileNotFoundError):
            grep_realisation({'options': '', 'pattern': 'pattern', 'path': 'nonexistent'})

    @patch('builtins.print')
    @patch('src.sub_functions.grep_dependences.Path')
    def test_grep_realisation_permission_error(self, mock_path, mock_print):
        """Тест с ошибкой доступа к файлу"""
        mock_file = self._create_mock_file('protected.txt')
        mock_path.return_value = mock_file

        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            grep_realisation({'options': '', 'pattern': 'pattern', 'path': 'protected.txt'})

        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        self.assertIn('Ошибка чтения файла', call_args)
        self.assertIn('protected.txt', call_args)

    @patch('src.sub_functions.grep_dependences.Path')
    def test_grep_realisation_unicode_error_handling(self, mock_path):
        """Тест обработки файлов с проблемной кодировкой"""
        mock_file = self._create_mock_file('binary.txt')
        mock_path.return_value = mock_file

        with patch('builtins.open', mock_open(read_data='\xff\xfebinary\x00data\x00\n')):
            grep_realisation({'options': '', 'pattern': 'pattern', 'path': 'binary.txt'})


if __name__ == '__main__':
    unittest.main()
