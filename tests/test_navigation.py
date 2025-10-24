"""
Тесты навигационных команд: cd и ls
"""
import unittest
from unittest.mock import patch, MagicMock, call
from pathlib import Path

# Импортируем тестируемые функции
from src.sub_functions.cd_dependences import cd_args_parse, cd_realisation
from src.sub_functions.ls_dependences import ls_args_parse, ls_realisation, detailed_list, check_access_rights


class TestCdCommands(unittest.TestCase):
    """Тесты для команды cd"""

    # ТЕСТЫ ДЛЯ cd_args_parse
    def test_cd_args_parse_no_args(self):
        """Тест cd_args_parse без аргументов - должен выбросить исключение"""
        with self.assertRaises(Exception) as context:
            cd_args_parse([])

        # Проверяем что функция выбросила исключение
        self.assertEqual(str(context.exception), "Для команды cd ожидается аргумент - path")

    def test_cd_args_parse_empty_string_arg(self):
        """Тест cd_args_parse с пустой строкой - должен выбросить исключение"""
        with self.assertRaises(Exception) as context:
            cd_args_parse([''])

        # Проверяем сообщение исключения
        self.assertEqual(str(context.exception), "Путь не может быть пустой строкой")

    @patch('src.sub_functions.cd_dependences.os.path.expanduser')
    def test_cd_args_parse_home_directory(self, mock_expanduser):
        """Тест cd_args_parse с домашним каталогом ~"""
        mock_expanduser.return_value = '/home/testuser'

        result = cd_args_parse(['~'])

        # Проверяем что возвращается правильный Path
        self.assertIsInstance(result, Path)
        self.assertEqual(str(result), '/home/testuser')
        mock_expanduser.assert_called_once_with('~')

    @patch('src.sub_functions.cd_dependences.Path')
    def test_cd_args_parse_nonexistent_path(self, mock_path):
        """Тест cd_args_parse с несуществующим путем - должен выбросить исключение"""
        # Настраиваем мок Path
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path_instance.__str__ = lambda x: '/nonexistent/path'
        mock_path.return_value = mock_path_instance

        with self.assertRaises(Exception) as context:
            cd_args_parse(['/nonexistent/path'])

        # Проверяем сообщение исключения
        self.assertEqual(str(context.exception), "Директория /nonexistent/path не существует")

    @patch('src.sub_functions.cd_dependences.Path')
    def test_cd_args_parse_file_instead_of_directory(self, mock_path):
        """Тест cd_args_parse с путем к файлу (не директории) - должен выбросить исключение"""
        # Настраиваем мок Path - путь существует, но это файл
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_dir.return_value = False
        mock_path_instance.__str__ = lambda x: '/some/file.txt'
        mock_path.return_value = mock_path_instance

        with self.assertRaises(Exception) as context:
            cd_args_parse(['/some/file.txt'])

        # Проверяем сообщение исключения
        self.assertEqual(str(context.exception), "/some/file.txt не является директорией")

    @patch('src.sub_functions.cd_dependences.Path')
    def test_cd_args_parse_valid_directory(self, mock_path):
        """Тест cd_args_parse с валидной директорией"""
        # Настраиваем мок Path - валидная директория
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_dir.return_value = True
        mock_path.return_value = mock_path_instance

        result = cd_args_parse(['/valid/directory'])

        # Проверяем что возвращается Path объект
        self.assertEqual(result, mock_path_instance)

    # ТЕСТЫ ДЛЯ cd_realisation
    @patch('src.sub_functions.cd_dependences.os')
    def test_cd_realisation_home_directory_success(self, mock_os):
        """Тест cd_realisation с домашним каталогом ~ - успешный случай"""
        mock_os.path.expanduser.return_value = '/home/testuser'

        # Не должно быть исключений
        cd_realisation('~')

        # Проверяем вызовы
        mock_os.path.expanduser.assert_called_once_with('~')
        mock_os.chdir.assert_called_once_with('/home/testuser')

    @patch('src.sub_functions.cd_dependences.os')
    def test_cd_realisation_normal_path_success(self, mock_os):
        """Тест cd_realisation с обычным путем - успешный случай"""
        mock_os.path.abspath.return_value = '/absolute/path'

        # Не должно быть исключений
        cd_realisation('/some/path')

        # Проверяем вызовы
        mock_os.path.abspath.assert_called_once_with('/some/path')
        mock_os.chdir.assert_called_once_with('/absolute/path')

    @patch('src.sub_functions.cd_dependences.os')
    def test_cd_realisation_permission_error(self, mock_os):
        """Тест cd_realisation с ошибкой прав доступа - должен пробросить исключение"""
        mock_os.chdir.side_effect = PermissionError("Access denied")
        mock_os.path.abspath.return_value = '/restricted/path'

        with self.assertRaises(PermissionError):
            cd_realisation('/restricted/path')

    @patch('src.sub_functions.cd_dependences.os')
    def test_cd_realisation_file_not_found_error(self, mock_os):
        """Тест cd_realisation с ошибкой файл не найден - должен пробросить исключение"""
        mock_os.chdir.side_effect = FileNotFoundError("No such file")
        mock_os.path.abspath.return_value = '/nonexistent/path'

        with self.assertRaises(FileNotFoundError):
            cd_realisation('/nonexistent/path')

    @patch('src.sub_functions.cd_dependences.os')
    def test_cd_realisation_general_exception(self, mock_os):
        """Тест cd_realisation с общей ошибкой - должен пробросить исключение"""
        mock_os.chdir.side_effect = Exception("Unexpected error")
        mock_os.path.abspath.return_value = '/some/path'

        with self.assertRaises(Exception):
            cd_realisation('/some/path')


class TestLsCommands(unittest.TestCase):
    """Тесты для команды ls"""

    # Тесты для ls_args_parse
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

    # Тесты для check_access_rights
    def test_check_access_rights(self):
        """Тест определения прав доступа"""
        mock_stat = MagicMock()
        mock_stat.st_mode = 0o100755  # rwxr-xr-x
        result = check_access_rights(mock_stat)
        self.assertEqual(result, "rwxr-xr-x")

    # Тесты для detailed_list
    @patch('src.sub_functions.ls_dependences.print')
    @patch('src.sub_functions.ls_dependences.datetime')
    @patch('src.sub_functions.ls_dependences.stat')
    def test_detailed_list_normal_file(self, mock_stat, mock_datetime, mock_print):
        """Тест детального вывода для обычного файла"""
        # Настройка моков
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

        # Вызов функции - не должно быть исключений
        detailed_list([mock_file])

        # Проверка вывода
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        self.assertIn('test.txt', call_args)
        self.assertIn('1024', call_args)

    @patch('src.sub_functions.ls_dependences.print')
    @patch('src.sub_functions.ls_dependences.datetime')
    @patch('src.sub_functions.ls_dependences.os.readlink')
    @patch('src.sub_functions.ls_dependences.stat')
    def test_detailed_list_symlink(self, mock_stat, mock_readlink, mock_datetime, mock_print):
        """Тест детального вывода для симлинка"""
        # Настройка моков
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

        # Вызов функции - не должно быть исключений
        detailed_list([mock_file])

        # Проверка вывода симлинка
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        self.assertIn('symlink -> /target/path', call_args)

    @patch('src.sub_functions.ls_dependences.print')
    @patch('src.sub_functions.ls_dependences.stat')
    def test_detailed_list_broken_symlink(self, mock_stat, mock_print):
        """Тест детального вывода для битого симлинка"""
        mock_file = MagicMock(spec=Path)
        mock_file.name = 'broken_symlink'
        mock_file.stat.return_value.st_mode = 0o120755  # symlink
        mock_file.stat.return_value.st_nlink = 1
        mock_file.stat.return_value.st_uid = 1000
        mock_file.stat.return_value.st_gid = 1000
        mock_file.stat.return_value.st_size = 64
        mock_file.stat.return_value.st_mtime = 1600000000.0
        mock_stat.S_ISLNK.return_value = True

        # Мокаем os.readlink чтобы выбросить OSError
        with patch('src.sub_functions.ls_dependences.os.readlink', side_effect=OSError("Broken link")):
            with patch('src.sub_functions.ls_dependences.datetime') as mock_datetime:
                mock_datetime.fromtimestamp.return_value.strftime.return_value = '2024-01-15 10:00:00'

                # Вызов функции - не должно быть исключений, должна обработать битую ссылку
                detailed_list([mock_file])

        # Проверяем вывод для битого симлинка
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        self.assertIn('broken_symlink -> [broken link]', call_args)

    @patch('src.sub_functions.ls_dependences.stat')
    def test_detailed_list_os_error(self, mock_stat):
        """Тест детального вывода при ошибке OS - должно выбросить исключение"""
        mock_file = MagicMock(spec=Path)
        mock_file.name = 'problem_file'
        mock_file.stat.side_effect = OSError("Permission denied")
        mock_stat.S_ISLNK.return_value = False

        # Должно выбросить OSError
        with self.assertRaises(OSError):
            detailed_list([mock_file])

    @patch('src.sub_functions.ls_dependences.stat')
    def test_detailed_list_general_error(self, mock_stat):
        """Тест детального вывода при общей ошибке - должно выбросить исключение"""
        mock_file = MagicMock(spec=Path)
        mock_file.name = 'corrupted_file'
        mock_file.stat.side_effect = Exception("Unexpected error")
        mock_stat.S_ISLNK.return_value = False

        # Должно выбросить Exception
        with self.assertRaises(Exception):
            detailed_list([mock_file])

    # Тесты для ls_realisation
    @patch('src.sub_functions.ls_dependences.print')
    @patch('src.sub_functions.ls_dependences.Path')
    @patch('src.sub_functions.ls_dependences.stat')
    def test_ls_realisation_current_dir_success(self, mock_stat, mock_path, mock_print):
        """Тест ls для текущей директории - успешный случай"""
        # Настраиваем мок для текущей директории
        mock_cwd = MagicMock()
        mock_cwd.exists.return_value = True
        mock_cwd.is_file.return_value = False
        mock_cwd.iterdir.return_value = [
            self._create_mock_file('file1.txt', is_dir=False, is_symlink=False),
            self._create_mock_file('folder1', is_dir=True, is_symlink=False)
        ]
        mock_path.cwd.return_value = mock_cwd

        # Настраиваем stat для определения типа файлов
        mock_stat.S_ISDIR.side_effect = lambda mode: mode == 0o040755
        mock_stat.S_ISLNK.side_effect = lambda mode: mode == 0o120755

        # Вызов функции - не должно быть исключений
        ls_realisation('', False)

        # Проверка вызовов print
        self.assertEqual(mock_print.call_count, 2)
        calls = [call('file1.txt'), call('folder1/')]
        mock_print.assert_has_calls(calls, any_order=True)

    @patch('src.sub_functions.ls_dependences.print')
    @patch('src.sub_functions.ls_dependences.Path')
    @patch('src.sub_functions.ls_dependences.stat')
    @patch('src.sub_functions.ls_dependences.os.access')
    def test_ls_realisation_executable_file_success(self, mock_access, mock_stat, mock_path, mock_print):
        """Тест ls для исполняемого файла - успешный случай"""
        # Настраиваем моки
        mock_path_obj = MagicMock()
        mock_path_obj.exists.return_value = True
        mock_path_obj.is_file.return_value = False
        mock_path_obj.iterdir.return_value = [
            self._create_mock_file('script.sh', is_dir=False, is_symlink=False)
        ]
        mock_path.return_value = mock_path_obj

        mock_stat.S_ISDIR.return_value = False
        mock_stat.S_ISLNK.return_value = False
        mock_access.return_value = True  # Файл исполняемый

        # Вызов функции - не должно быть исключений
        ls_realisation('/some/path', False)

        # Проверка вывода с *
        mock_print.assert_called_once_with('script.sh*')

    @patch('src.sub_functions.ls_dependences.print')
    @patch('src.sub_functions.ls_dependences.Path')
    @patch('src.sub_functions.ls_dependences.stat')
    def test_ls_realisation_symlink_file_success(self, mock_stat, mock_path, mock_print):
        """Тест ls для симлинка - успешный случай"""
        # Настраиваем моки
        mock_path_obj = MagicMock()
        mock_path_obj.exists.return_value = True
        mock_path_obj.is_file.return_value = False
        mock_path_obj.iterdir.return_value = [
            self._create_mock_file('symlink', is_dir=False, is_symlink=True)
        ]
        mock_path.return_value = mock_path_obj

        mock_stat.S_ISDIR.return_value = False
        mock_stat.S_ISLNK.side_effect = lambda mode: mode == 0o120755

        # Вызов функции - не должно быть исключений
        ls_realisation('/some/path', False)

        # Проверка вывода с @
        mock_print.assert_called_once_with('symlink@')

    @patch('src.sub_functions.ls_dependences.Path')
    def test_ls_realisation_nonexistent_path(self, mock_path):
        """Тест ls с несуществующим путем - должно выбросить исключение"""
        # Настраиваем моки
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path_instance.__str__ = lambda x: '/nonexistent/path'
        mock_path.return_value = mock_path_instance

        # Должно выбросить исключение
        with self.assertRaises(Exception) as context:
            ls_realisation('/nonexistent/path', False)

        # Проверяем сообщение исключения
        self.assertEqual(str(context.exception), "Нет такого файла/директории, /nonexistent/path")

    @patch('src.sub_functions.ls_dependences.Path')
    def test_ls_realisation_permission_error_on_iterdir(self, mock_path):
        """Тест ls с ошибкой прав доступа при итерации - должно выбросить исключение"""
        # Настраиваем моки
        mock_path_obj = MagicMock()
        mock_path_obj.exists.return_value = True
        mock_path_obj.is_file.return_value = False
        mock_path_obj.iterdir.side_effect = PermissionError("Access denied")
        mock_path.return_value = mock_path_obj

        # Должно выбросить PermissionError
        with self.assertRaises(PermissionError):
            ls_realisation('/restricted/path', False)

    @patch('src.sub_functions.ls_dependences.detailed_list')
    @patch('src.sub_functions.ls_dependences.Path')
    @patch('src.sub_functions.ls_dependences.stat')
    def test_ls_realisation_with_long_flag_success(self, mock_stat, mock_path, mock_detailed_list):
        """Тест ls с флагом -l - успешный случай"""
        # Настраиваем моки
        mock_path_obj = MagicMock()
        mock_path_obj.exists.return_value = True
        mock_path_obj.is_file.return_value = False
        mock_path_obj.iterdir.return_value = [
            self._create_mock_file('file1.txt', is_dir=False, is_symlink=False)
        ]
        mock_path.return_value = mock_path_obj

        mock_stat.S_ISDIR.return_value = False
        mock_stat.S_ISLNK.return_value = False

        # Вызов функции с флагом -l - не должно быть исключений
        ls_realisation('/some/path', True)

        # Проверка вызова detailed_list
        mock_detailed_list.assert_called_once()

    @patch('src.sub_functions.ls_dependences.print')
    @patch('src.sub_functions.ls_dependences.Path')
    @patch('src.sub_functions.ls_dependences.stat')
    def test_ls_realisation_hidden_files_skipped(self, mock_stat, mock_path, mock_print):
        """Тест что скрытые файлы пропускаются - успешный случай"""
        # Настраиваем моки
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

        # Вызов функции - не должно быть исключений
        ls_realisation('', False)

        # Проверка что выведен только visible_file
        mock_print.assert_called_once_with('visible_file')

    @patch('src.sub_functions.ls_dependences.Path')
    @patch('src.sub_functions.ls_dependences.stat')
    def test_ls_realisation_file_access_error(self, mock_stat, mock_path):
        """Тест ls с ошибкой доступа к отдельному файлу - должно выбросить исключение"""
        # Настраиваем моки
        mock_cwd = MagicMock()
        mock_cwd.exists.return_value = True
        mock_cwd.is_file.return_value = False

        # Создаем файл, который выбросит исключение при stat
        problematic_file = self._create_mock_file('problem_file', is_dir=False, is_symlink=False)
        problematic_file.stat.side_effect = OSError("Access denied")

        mock_cwd.iterdir.return_value = [
            self._create_mock_file('good_file', is_dir=False, is_symlink=False),
            problematic_file
        ]
        mock_path.cwd.return_value = mock_cwd

        mock_stat.S_ISDIR.return_value = False
        mock_stat.S_ISLNK.return_value = False

        # Должно выбросить OSError при обработке problem_file
        with self.assertRaises(OSError):
            ls_realisation('', False)

    @patch('src.sub_functions.ls_dependences.print')
    @patch('src.sub_functions.ls_dependences.Path')
    @patch('src.sub_functions.ls_dependences.stat')
    def test_ls_realisation_single_file_success(self, mock_stat, mock_path, mock_print):
        """Тест ls для одного файла (не директории) - успешный случай"""
        # Настраиваем моки - путь указывает на файл
        mock_file_path = MagicMock()
        mock_file_path.exists.return_value = True
        mock_file_path.is_file.return_value = True
        mock_file_path.name = 'single_file.txt'
        mock_path.return_value = mock_file_path

        # Мокаем stat для файла
        mock_stat_result = MagicMock()
        mock_stat_result.st_mode = 0o100644
        mock_stat.S_ISDIR.return_value = False
        mock_stat.S_ISLNK.return_value = False
        mock_file_path.stat.return_value = mock_stat_result

        # Вызов функции - не должно быть исключений
        ls_realisation('/path/to/file.txt', False)

        # Проверка что выведен файл
        mock_print.assert_called_once_with('single_file.txt')

    @patch('src.sub_functions.ls_dependences.detailed_list')
    @patch('src.sub_functions.ls_dependences.Path')
    def test_ls_realisation_single_file_with_long_flag(self, mock_path, mock_detailed_list):
        """Тест ls для одного файла с флагом -l - успешный случай"""
        # Настраиваем моки - путь указывает на файл
        mock_file_path = MagicMock()
        mock_file_path.exists.return_value = True
        mock_file_path.is_file.return_value = True
        mock_file_path.name = 'single_file.txt'
        mock_path.return_value = mock_file_path

        # Вызов функции с флагом -l - не должно быть исключений
        ls_realisation('/path/to/file.txt', True)

        # Проверка что вызван detailed_list с одним файлом
        mock_detailed_list.assert_called_once()
        call_args = mock_detailed_list.call_args[0][0]
        self.assertEqual(len(call_args), 1)
        self.assertEqual(call_args[0], mock_file_path)

    # Вспомогательный метод для создания мок-файлов
    @staticmethod
    def _create_mock_file(name, is_dir=False, is_symlink=False):
        """Создает мок файла с заданными характеристиками"""
        mock_file = MagicMock(spec=Path)
        mock_file.name = name

        # Настраиваем stat в зависимости от типа файла
        mock_stat = MagicMock()
        if is_dir:
            mock_stat.st_mode = 0o040755  # directory
        elif is_symlink:
            mock_stat.st_mode = 0o120755  # symlink
        else:
            mock_stat.st_mode = 0o100644  # regular file

        mock_file.stat.return_value = mock_stat
        return mock_file


class TestNavigationIntegration(unittest.TestCase):
    """Интеграционные тесты для взаимодействия команд навигации"""

    @patch('src.sub_functions.cd_dependences.os')
    @patch('src.sub_functions.ls_dependences.Path')
    @patch('src.sub_functions.ls_dependences.print')
    @patch('src.sub_functions.ls_dependences.stat')
    def test_cd_then_ls_sequence(self, mock_stat, mock_print, mock_path_ls, mock_os_cd):
        """Тест последовательности команд: cd затем ls"""
        # Настройка моков для cd
        mock_os_cd.path.abspath.return_value = '/new/directory'

        # Настройка моков для ls
        mock_dir = MagicMock()
        mock_dir.exists.return_value = True
        mock_dir.is_file.return_value = False

        # Создаем реальные моки файлов
        mock_file1 = MagicMock(spec=Path)
        mock_file1.name = 'file1.txt'
        mock_file1.stat.return_value.st_mode = 0o100644

        mock_file2 = MagicMock(spec=Path)
        mock_file2.name = 'dir1'
        mock_file2.stat.return_value.st_mode = 0o040755

        mock_dir.iterdir.return_value = [mock_file1, mock_file2]
        mock_path_ls.return_value = mock_dir

        # Настройка stat для ls
        mock_stat.S_ISDIR.side_effect = lambda mode: mode == 0o040755
        mock_stat.S_ISLNK.return_value = False

        # Выполняем последовательность команд
        cd_realisation('/new/directory')
        ls_realisation('/new/directory', False)

        # Проверяем вызовы
        mock_os_cd.chdir.assert_called_once_with('/new/directory')
        mock_path_ls.assert_called_with('/new/directory')
        self.assertEqual(mock_print.call_count, 2)


if __name__ == '__main__':
    unittest.main()
