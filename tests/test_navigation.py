import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from src.sub_functions.cd_dependences import cd_args_parse, cd_realisation
from src.sub_functions.ls_dependences import ls_args_parse, ls_realisation, detailed_list, check_access_rights

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

"""
Тесты навигационных команд: cd, ls и grep
"""

class TestCdCommands(unittest.TestCase):
    """Тесты для команды изменения директории cd"""

    def test_cd_args_parse_no_args(self):
        """Тест парсинга аргументов cd без аргументов"""
        with self.assertRaises(Exception) as context:
            cd_args_parse([])
        self.assertEqual(str(context.exception), "Для команды cd ожидается аргумент - path")

    def test_cd_args_parse_empty_string_arg(self):
        """Тест парсинга аргументов cd с пустой строкой"""
        with self.assertRaises(Exception) as context:
            cd_args_parse([''])
        self.assertEqual(str(context.exception), "Путь не может быть пустой строкой")

    @patch('src.sub_functions.cd_dependences.os.path.expanduser')
    def test_cd_args_parse_home_directory(self, mock_expanduser):
        """Тест парсинга аргументов cd с домашним каталогом"""
        mock_expanduser.return_value = '/home/testuser'
        result = cd_args_parse(['~'])
        self.assertIsInstance(result, Path)
        self.assertEqual(str(result), '/home/testuser')
        mock_expanduser.assert_called_once_with('~')

    @patch('src.sub_functions.cd_dependences.Path')
    def test_cd_args_parse_nonexistent_path(self, mock_path):
        """Тест парсинга аргументов cd с несуществующим путем"""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path_instance.__str__ = lambda x: '/nonexistent/path'
        mock_path.return_value = mock_path_instance

        with self.assertRaises(Exception) as context:
            cd_args_parse(['/nonexistent/path'])
        self.assertEqual(str(context.exception), "Директория /nonexistent/path не существует")

    @patch('src.sub_functions.cd_dependences.Path')
    def test_cd_args_parse_file_instead_of_directory(self, mock_path):
        """Тест парсинга аргументов cd с путем к файлу вместо директории"""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_dir.return_value = False
        mock_path_instance.__str__ = lambda x: '/some/file.txt'
        mock_path.return_value = mock_path_instance

        with self.assertRaises(Exception) as context:
            cd_args_parse(['/some/file.txt'])
        self.assertEqual(str(context.exception), "/some/file.txt не является директорией")

    @patch('src.sub_functions.cd_dependences.Path')
    def test_cd_args_parse_valid_directory(self, mock_path):
        """Тест парсинга аргументов cd с валидной директорией"""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_dir.return_value = True
        mock_path.return_value = mock_path_instance

        result = cd_args_parse(['/valid/directory'])
        self.assertEqual(result, mock_path_instance)

    @patch('src.sub_functions.cd_dependences.os')
    def test_cd_realisation_home_directory_success(self, mock_os):
        """Тест выполнения cd с домашним каталогом"""
        mock_os.path.expanduser.return_value = '/home/testuser'
        cd_realisation('~')
        mock_os.path.expanduser.assert_called_once_with('~')
        mock_os.chdir.assert_called_once_with('/home/testuser')

    @patch('src.sub_functions.cd_dependences.os')
    def test_cd_realisation_normal_path_success(self, mock_os):
        """Тест выполнения cd с обычным путем"""
        mock_os.path.abspath.return_value = '/absolute/path'
        cd_realisation('/some/path')
        mock_os.path.abspath.assert_called_once_with('/some/path')
        mock_os.chdir.assert_called_once_with('/absolute/path')

    @patch('builtins.print')
    @patch('src.sub_functions.cd_dependences.os')
    def test_cd_realisation_permission_error(self, mock_os, _):
        """Тест выполнения cd с ошибкой прав доступа"""
        mock_os.chdir.side_effect = PermissionError("Access denied")
        mock_os.path.abspath.return_value = '/restricted/path'

        with self.assertRaises(PermissionError):
            cd_realisation('/restricted/path')

    @patch('builtins.print')
    @patch('src.sub_functions.cd_dependences.os')
    def test_cd_realisation_file_not_found_error(self, mock_os, _):
        """Тест выполнения cd с ошибкой файл не найден"""
        mock_os.chdir.side_effect = FileNotFoundError("No such file")
        mock_os.path.abspath.return_value = '/nonexistent/path'

        with self.assertRaises(FileNotFoundError):
            cd_realisation('/nonexistent/path')

    @patch('builtins.print')
    @patch('src.sub_functions.cd_dependences.os')
    def test_cd_realisation_general_exception(self, mock_os, _):
        """Тест выполнения cd с общей ошибкой"""
        mock_os.chdir.side_effect = Exception("Unexpected error")
        mock_os.path.abspath.return_value = '/some/path'

        with self.assertRaises(Exception):
            cd_realisation('/some/path')


class TestLsCommands(unittest.TestCase):
    """Тесты для команды списка файлов ls"""

    def test_ls_args_parse_no_args(self):
        """Тест парсинга аргументов ls без аргументов"""
        result = ls_args_parse([])
        expected = {'path': '', 'long': False}
        self.assertEqual(result, expected)

    def test_ls_args_parse_with_path(self):
        """Тест парсинга аргументов ls с путем"""
        result = ls_args_parse(['/some/path'])
        expected = {'path': '/some/path', 'long': False}
        self.assertEqual(result, expected)

    def test_ls_args_parse_with_long_flag(self):
        """Тест парсинга аргументов ls с флагом -l"""
        result = ls_args_parse(['-l'])
        expected = {'path': '', 'long': True}
        self.assertEqual(result, expected)

    def test_ls_args_parse_with_path_and_long(self):
        """Тест парсинга аргументов ls с путем и флагом -l"""
        result = ls_args_parse(['-l', '/some/path'])
        expected = {'path': '/some/path', 'long': True}
        self.assertEqual(result, expected)

    def test_check_access_rights(self):
        """Тест определения прав доступа к файлу"""
        mock_stat = MagicMock()
        mock_stat.st_mode = 0o100755
        result = check_access_rights(mock_stat)
        self.assertEqual(result, "rwxr-xr-x")

    @patch('src.sub_functions.ls_dependences.print')
    @patch('src.sub_functions.ls_dependences.datetime')
    @patch('src.sub_functions.ls_dependences.stat')
    def test_detailed_list_normal_file(self, mock_stat, mock_datetime, mock_print):
        """Тест детального вывода для обычного файла"""
        mock_datetime.fromtimestamp.return_value.strftime.return_value = '2024-01-15 10:00:00'
        mock_stat.S_ISLNK.return_value = False

        mock_file = MagicMock(spec=Path)
        mock_file.name = 'test.txt'
        mock_file.stat.return_value.st_mode = 0o100644
        mock_file.stat.return_value.st_nlink = 1
        mock_file.stat.return_value.st_uid = 1000
        mock_file.stat.return_value.st_gid = 1000
        mock_file.stat.return_value.st_size = 1024
        mock_file.stat.return_value.st_mtime = 1600000000.0

        detailed_list([mock_file])
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        self.assertIn('test.txt', call_args)
        self.assertIn('1024', call_args)

    @patch('src.sub_functions.ls_dependences.print')
    @patch('src.sub_functions.ls_dependences.datetime')
    @patch('src.sub_functions.ls_dependences.os.readlink')
    @patch('src.sub_functions.ls_dependences.stat')
    def test_detailed_list_symlink(self, mock_stat, mock_readlink, mock_datetime, mock_print):
        """Тест детального вывода для сиволической ссылки"""
        mock_datetime.fromtimestamp.return_value.strftime.return_value = '2024-01-15 10:00:00'
        mock_readlink.return_value = '/target/path'
        mock_stat.S_ISLNK.return_value = True

        mock_file = MagicMock(spec=Path)
        mock_file.name = 'symlink'
        mock_file.stat.return_value.st_mode = 0o120755
        mock_file.stat.return_value.st_nlink = 1
        mock_file.stat.return_value.st_uid = 1000
        mock_file.stat.return_value.st_gid = 1000
        mock_file.stat.return_value.st_size = 64
        mock_file.stat.return_value.st_mtime = 1600000000.0

        detailed_list([mock_file])
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        self.assertIn('symlink -> /target/path', call_args)

    @patch('src.sub_functions.ls_dependences.print')
    @patch('src.sub_functions.ls_dependences.stat')
    def test_detailed_list_broken_symlink(self, mock_stat, mock_print):
        """Тест детального вывода для битой символической ссылки"""
        mock_file = MagicMock(spec=Path)
        mock_file.name = 'broken_symlink'
        mock_file.stat.return_value.st_mode = 0o120755
        mock_file.stat.return_value.st_nlink = 1
        mock_file.stat.return_value.st_uid = 1000
        mock_file.stat.return_value.st_gid = 1000
        mock_file.stat.return_value.st_size = 64
        mock_file.stat.return_value.st_mtime = 1600000000.0
        mock_stat.S_ISLNK.return_value = True

        with patch('src.sub_functions.ls_dependences.os.readlink', side_effect=OSError("Broken link")):
            with patch('src.sub_functions.ls_dependences.datetime') as mock_datetime:
                mock_datetime.fromtimestamp.return_value.strftime.return_value = '2024-01-15 10:00:00'
                detailed_list([mock_file])

        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        self.assertIn('broken_symlink -> [broken link]', call_args)

    @patch('src.sub_functions.ls_dependences.stat')
    def test_detailed_list_os_error(self, mock_stat):
        """Тест детального вывода при ошибке OS"""
        mock_file = MagicMock(spec=Path)
        mock_file.name = 'problem_file'
        mock_file.stat.side_effect = OSError("Permission denied")
        mock_stat.S_ISLNK.return_value = False

        with self.assertRaises(OSError):
            detailed_list([mock_file])

    @patch('src.sub_functions.ls_dependences.stat')
    def test_detailed_list_general_error(self, mock_stat):
        """Тест детального вывода при общей ошибке"""
        mock_file = MagicMock(spec=Path)
        mock_file.name = 'corrupted_file'
        mock_file.stat.side_effect = Exception("Unexpected error")
        mock_stat.S_ISLNK.return_value = False

        with self.assertRaises(Exception):
            detailed_list([mock_file])

    @patch('src.sub_functions.ls_dependences.print')
    @patch('src.sub_functions.ls_dependences.Path')
    @patch('src.sub_functions.ls_dependences.stat')
    def test_ls_realisation_current_dir_success(self, mock_stat, mock_path, mock_print):
        """Тест ls для текущей директории"""
        mock_cwd = MagicMock()
        mock_cwd.exists.return_value = True
        mock_cwd.is_file.return_value = False
        mock_cwd.iterdir.return_value = [
            self._create_mock_file('file1.txt', is_dir=False, is_symlink=False),
            self._create_mock_file('folder1', is_dir=True, is_symlink=False)
        ]
        mock_path.cwd.return_value = mock_cwd

        mock_stat.S_ISDIR.side_effect = lambda mode: mode == 0o040755
        mock_stat.S_ISLNK.side_effect = lambda mode: mode == 0o120755

        ls_realisation('', False)
        self.assertEqual(mock_print.call_count, 2)
        calls = [call('file1.txt'), call('folder1/')]
        mock_print.assert_has_calls(calls, any_order=True)

    @patch('src.sub_functions.ls_dependences.print')
    @patch('src.sub_functions.ls_dependences.Path')
    @patch('src.sub_functions.ls_dependences.stat')
    @patch('src.sub_functions.ls_dependences.os.access')
    def test_ls_realisation_executable_file_success(self, mock_access, mock_stat, mock_path, mock_print):
        """Тест ls для исполняемого файла"""
        mock_path_obj = MagicMock()
        mock_path_obj.exists.return_value = True
        mock_path_obj.is_file.return_value = False
        mock_path_obj.iterdir.return_value = [
            self._create_mock_file('script.sh', is_dir=False, is_symlink=False)
        ]
        mock_path.return_value = mock_path_obj

        mock_stat.S_ISDIR.return_value = False
        mock_stat.S_ISLNK.return_value = False
        mock_access.return_value = True

        ls_realisation('/some/path', False)
        mock_print.assert_called_once_with('script.sh*')

    @patch('src.sub_functions.ls_dependences.print')
    @patch('src.sub_functions.ls_dependences.Path')
    @patch('src.sub_functions.ls_dependences.stat')
    def test_ls_realisation_symlink_file_success(self, mock_stat, mock_path, mock_print):
        """Тест ls для символической ссылки"""
        mock_path_obj = MagicMock()
        mock_path_obj.exists.return_value = True
        mock_path_obj.is_file.return_value = False
        mock_path_obj.iterdir.return_value = [
            self._create_mock_file('symlink', is_dir=False, is_symlink=True)
        ]
        mock_path.return_value = mock_path_obj

        mock_stat.S_ISDIR.return_value = False
        mock_stat.S_ISLNK.side_effect = lambda mode: mode == 0o120755

        ls_realisation('/some/path', False)
        mock_print.assert_called_once_with('symlink@')

    @patch('src.sub_functions.ls_dependences.Path')
    def test_ls_realisation_nonexistent_path(self, mock_path):
        """Тест ls с несуществующим путем"""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path_instance.__str__ = lambda x: '/nonexistent/path'
        mock_path.return_value = mock_path_instance

        with self.assertRaises(Exception) as context:
            ls_realisation('/nonexistent/path', False)
        self.assertEqual(str(context.exception), "Нет такого файла/директории, /nonexistent/path")

    @patch('src.sub_functions.ls_dependences.Path')
    def test_ls_realisation_permission_error_on_iterdir(self, mock_path):
        """Тест ls с ошибкой прав доступа при итерации"""
        mock_path_obj = MagicMock()
        mock_path_obj.exists.return_value = True
        mock_path_obj.is_file.return_value = False
        mock_path_obj.iterdir.side_effect = PermissionError("Access denied")
        mock_path.return_value = mock_path_obj

        with self.assertRaises(PermissionError):
            ls_realisation('/restricted/path', False)

    @patch('src.sub_functions.ls_dependences.detailed_list')
    @patch('src.sub_functions.ls_dependences.Path')
    @patch('src.sub_functions.ls_dependences.stat')
    def test_ls_realisation_with_long_flag_success(self, mock_stat, mock_path, mock_detailed_list):
        """Тест ls с флагом -l"""
        mock_path_obj = MagicMock()
        mock_path_obj.exists.return_value = True
        mock_path_obj.is_file.return_value = False
        mock_path_obj.iterdir.return_value = [
            self._create_mock_file('file1.txt', is_dir=False, is_symlink=False)
        ]
        mock_path.return_value = mock_path_obj

        mock_stat.S_ISDIR.return_value = False
        mock_stat.S_ISLNK.return_value = False

        ls_realisation('/some/path', True)
        mock_detailed_list.assert_called_once()

    @patch('src.sub_functions.ls_dependences.print')
    @patch('src.sub_functions.ls_dependences.Path')
    @patch('src.sub_functions.ls_dependences.stat')
    def test_ls_realisation_hidden_files_skipped(self, mock_stat, mock_path, mock_print):
        """Тест пропуска скрытых файлов в ls"""
        mock_cwd = MagicMock()
        mock_cwd.exists.return_value = True
        mock_cwd.is_file.return_value = False
        mock_cwd.iterdir.return_value = [
            self._create_mock_file('.hidden_file', is_dir=False, is_symlink=False),
            self._create_mock_file('visible_file', is_dir=False, is_symlink=False)
        ]
        mock_path.cwd.return_value = mock_cwd

        mock_stat.S_ISDIR.return_value = False
        mock_stat.S_ISLNK.return_value = False

        ls_realisation('', False)
        mock_print.assert_called_once_with('visible_file')

    @patch('src.sub_functions.ls_dependences.print')
    @patch('src.sub_functions.ls_dependences.Path')
    @patch('src.sub_functions.ls_dependences.stat')
    def test_ls_realisation_single_file_success(self, mock_stat, mock_path, mock_print):
        """Тест ls для одного файла"""
        mock_file_path = MagicMock()
        mock_file_path.exists.return_value = True
        mock_file_path.is_file.return_value = True
        mock_file_path.name = 'single_file.txt'
        mock_path.return_value = mock_file_path

        mock_stat_result = MagicMock()
        mock_stat_result.st_mode = 0o100644
        mock_stat.S_ISDIR.return_value = False
        mock_stat.S_ISLNK.return_value = False
        mock_file_path.stat.return_value = mock_stat_result

        ls_realisation('/path/to/file.txt', False)
        mock_print.assert_called_once_with('single_file.txt')

    @patch('src.sub_functions.ls_dependences.detailed_list')
    @patch('src.sub_functions.ls_dependences.Path')
    def test_ls_realisation_single_file_with_long_flag(self, mock_path, mock_detailed_list):
        """Тест ls для одного файла с флагом -l"""
        mock_file_path = MagicMock()
        mock_file_path.exists.return_value = True
        mock_file_path.is_file.return_value = True
        mock_file_path.name = 'single_file.txt'
        mock_path.return_value = mock_file_path

        ls_realisation('/path/to/file.txt', True)
        mock_detailed_list.assert_called_once()
        call_args = mock_detailed_list.call_args[0][0]
        self.assertEqual(len(call_args), 1)
        self.assertEqual(call_args[0], mock_file_path)

    @staticmethod
    def _create_mock_file(name, is_dir=False, is_symlink=False):
        """Создаем мок файла с заданными характеристиками"""
        mock_file = MagicMock(spec=Path)
        mock_file.name = name

        mock_stat = MagicMock()
        if is_dir:
            mock_stat.st_mode = 0o040755
        elif is_symlink:
            mock_stat.st_mode = 0o120755
        else:
            mock_stat.st_mode = 0o100644

        mock_file.stat.return_value = mock_stat
        return mock_file

if __name__ == '__main__':
    unittest.main()
