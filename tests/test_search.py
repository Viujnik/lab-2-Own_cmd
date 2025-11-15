import os
import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open, call
from src.sub_functions.grep_dependences import grep_args_parse, grep_realisation

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


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
        expected = {
            "path": 'file.txt',
            "recursive": False,
            "ignore_case": False,
            "pattern": 'pattern',
        }
        self.assertEqual(result, expected)

    def test_grep_args_parse_with_recursive(self):
        """Тест парсинга аргументов grep с рекурсивным поиском"""
        result = grep_args_parse(['-r', 'pattern', 'folder'])
        expected = {
            "path": 'folder',
            "recursive": True,
            "ignore_case": False,
            "pattern": 'pattern',
        }
        self.assertEqual(result, expected)

    def test_grep_args_parse_with_ignore_case(self):
        """Тест парсинга аргументов grep с игнорированием регистра"""
        result = grep_args_parse(['-i', 'pattern', 'file.txt'])
        expected = {
            "path": 'file.txt',
            "recursive": False,
            "ignore_case": True,
            "pattern": 'pattern',
        }
        self.assertEqual(result, expected)

    def test_grep_args_parse_with_both_flags(self):
        """Тест парсинга аргументов grep с обоими флагами"""
        result = grep_args_parse(['-r', '-i', 'pattern', 'folder'])
        expected = {
            "path": 'folder',
            "recursive": True,
            "ignore_case": True,
            "pattern": 'pattern',
        }
        self.assertEqual(result, expected)

    def test_grep_args_parse_flags_combined(self):
        """Тест парсинга аргументов grep с объединенными флагами"""
        result = grep_args_parse(['-ri', 'pattern', 'folder'])
        expected = {
            "path": 'folder',
            "recursive": True,
            "ignore_case": True,
            "pattern": 'pattern',
        }
        self.assertEqual(result, expected)

    def test_grep_args_parse_insufficient_args(self):
        """Тест парсинга аргументов grep с недостаточным количеством аргументов"""
        with self.assertRaises(Exception):
            grep_args_parse(['pattern'])

    def test_grep_args_parse_no_pattern(self):
        """Тест парсинга аргументов grep без шаблона"""
        with self.assertRaises(Exception):
            grep_args_parse(['-r', 'folder'])

    @patch('src.sub_functions.grep_dependences.print')
    @patch('src.sub_functions.grep_dependences.Path')
    def test_grep_realisation_file_search_success(self, mock_path, mock_print):
        """Тест поиска в файле"""
        mock_file = self._create_mock_file('test.txt')
        mock_path.return_value = mock_file

        with patch('builtins.open', mock_open(read_data='line1\npattern line2\nline3\n')):
            grep_realisation({
                'pattern': 'pattern',
                'path': 'test.txt',
                'recursive': False,
                'ignore_case': False
            })
        mock_print.assert_called_once_with('test.txt:2:pattern line2')

    @patch('src.sub_functions.grep_dependences.print')
    @patch('src.sub_functions.grep_dependences.Path')
    def test_grep_realisation_case_insensitive(self, mock_path, mock_print):
        """Тест поиска без учета регистра"""
        mock_file = self._create_mock_file('test.txt')
        mock_path.return_value = mock_file

        with patch('builtins.open', mock_open(read_data='LINE1\nPATTERN line2\nline3\n')):
            grep_realisation({
                'pattern': 'pattern',
                'path': 'test.txt',
                'recursive': False,
                'ignore_case': True
            })
        mock_print.assert_called_once_with('test.txt:2:PATTERN line2')

    @patch('src.sub_functions.grep_dependences.print')
    @patch('src.sub_functions.grep_dependences.Path')
    def test_grep_realisation_multiple_matches(self, mock_path, mock_print):
        """Тест поиска с несколькими совпадениями"""
        mock_file = self._create_mock_file('test.txt')
        mock_path.return_value = mock_file

        with patch('builtins.open', mock_open(read_data='pattern1\nline2\npattern3\npattern4\n')):
            grep_realisation({
                'pattern': 'pattern',
                'path': 'test.txt',
                'recursive': False,
                'ignore_case': False
            })

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
            grep_realisation({
                'pattern': 'pattern',
                'path': 'test.txt',
                'recursive': False,
                'ignore_case': False
            })

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
            grep_realisation({
                'pattern': 'pattern',
                'path': 'folder',
                'recursive': False,
                'ignore_case': False
            })
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
            grep_realisation({
                'pattern': 'pattern',
                'path': 'folder',
                'recursive': True,
                'ignore_case': False
            })
        self.assertEqual(mock_print.call_count, 2)

    def test_grep_realisation_invalid_pattern(self):
        """Тест с невалидным регулярным выражением"""
        with self.assertRaises(ValueError):
            grep_realisation({
                'pattern': '[invalid',
                'path': 'file.txt',
                'recursive': False,
                'ignore_case': False
            })

    @patch('src.sub_functions.grep_dependences.Path')
    def test_grep_realisation_file_not_found(self, mock_path):
        """Тест с несуществующим путем"""
        mock_path_obj = self._create_mock_file('nonexistent', is_file=False, is_dir=False)
        mock_path.return_value = mock_path_obj

        with self.assertRaises(FileNotFoundError):
            grep_realisation({
                'pattern': 'pattern',
                'path': 'nonexistent',
                'recursive': False,
                'ignore_case': False
            })

    @patch('builtins.print')
    @patch('src.sub_functions.grep_dependences.Path')
    def test_grep_realisation_permission_error(self, mock_path, mock_print):
        """Тест с ошибкой доступа к файлу"""
        mock_file = self._create_mock_file('protected.txt')
        mock_path.return_value = mock_file

        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            grep_realisation({
                'pattern': 'pattern',
                'path': 'protected.txt',
                'recursive': False,
                'ignore_case': False
            })

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
            grep_realisation({
                'pattern': 'pattern',
                'path': 'binary.txt',
                'recursive': False,
                'ignore_case': False
            })


if __name__ == '__main__':
    unittest.main()
