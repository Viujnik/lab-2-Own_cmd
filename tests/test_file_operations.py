"""
Тесты для файловых операций: cat
"""
import unittest
from unittest.mock import patch, MagicMock, mock_open

# Импортируем тестируемые функции
from src.sub_functions.cat_dependences import cat_args_parse, cat_realisation


class TestCatCommands(unittest.TestCase):
    """Тесты для команды cat"""

    # ТЕСТЫ ДЛЯ cat_args_parse
    def test_cat_args_parse_no_args(self):
        """Тест cat_args_parse без аргументов - должен выбросить исключение"""
        with self.assertRaises(Exception) as context:
            cat_args_parse([])

        # Проверяем что функция выбросила исключение
        self.assertEqual(str(context.exception), "Для команды cat ожидается 2-ой аргумент - файл или путь к файлу")

    def test_cat_args_parse_empty_string_arg(self):
        """Тест cat_args_parse с пустой строкой - должен выбросить исключение"""
        with self.assertRaises(Exception) as context:
            cat_args_parse([''])

        # Проверяем сообщение исключения
        self.assertEqual(str(context.exception), "Для команды cat ожидается 2-ой аргумент - файл или путь к файлу")

    @patch('src.sub_functions.cat_dependences.Path')
    def test_cat_args_parse_directory_path(self, mock_path):
        """Тест cat_args_parse с путем к директории - должен выбросить исключение"""
        # Настраиваем мок Path - путь существует и является директорией
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_dir.return_value = True
        mock_path_instance.is_symlink.return_value = False
        mock_path.return_value = mock_path_instance

        with self.assertRaises(Exception) as context:
            cat_args_parse(['/some/directory'])

        # Проверяем сообщение исключения
        self.assertEqual(str(context.exception), "Для команды cat нужно передать файл или путь к файлу")

    @patch('src.sub_functions.cat_dependences.Path')
    def test_cat_args_parse_symlink_path(self, mock_path):
        """Тест cat_args_parse с путем к симлинку - должен выбросить исключение"""
        # Настраиваем мок Path - путь существует и является симлинком
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_dir.return_value = False
        mock_path_instance.is_symlink.return_value = True
        mock_path.return_value = mock_path_instance

        with self.assertRaises(Exception) as context:
            cat_args_parse(['/some/symlink'])

        # Проверяем сообщение исключения
        self.assertEqual(str(context.exception), "Для команды cat нужно передать файл или путь к файлу")

    @patch('src.sub_functions.cat_dependences.Path')
    def test_cat_args_parse_nonexistent_path(self, mock_path):
        """Тест cat_args_parse с несуществующим путем - должен выбросить FileNotFoundError"""
        # Настраиваем мок Path - путь не существует
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance

        with self.assertRaises(FileNotFoundError):
            cat_args_parse(['/nonexistent/file'])

    @patch('src.sub_functions.cat_dependences.Path')
    def test_cat_args_parse_valid_file(self, mock_path):
        """Тест cat_args_parse с валидным файлом - должен вернуть Path"""
        # Настраиваем мок Path - валидный файл
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_dir.return_value = False
        mock_path_instance.is_symlink.return_value = False
        mock_path.return_value = mock_path_instance

        result = cat_args_parse(['/valid/file.txt'])

        # Проверяем что возвращается Path объект
        self.assertEqual(result, mock_path_instance)

    # ТЕСТЫ ДЛЯ cat_realisation
    @patch('src.sub_functions.cat_dependences.print')
    @patch('src.sub_functions.cat_dependences.Path')
    def test_cat_realisation_success(self, mock_path, mock_print):
        """Тест cat_realisation с валидным файлом - успешный случай"""
        # Настраиваем мок Path и файла
        mock_file_path = MagicMock()
        mock_path.return_value = mock_file_path

        # Мокаем открытие файла и чтение
        mock_file_content = "Hello, World!\nThis is a test file."
        with patch('builtins.open', mock_open(read_data=mock_file_content)) as mock_file:
            # Вызов функции - не должно быть исключений
            cat_realisation('/valid/file.txt')

            # Проверяем вызовы
            mock_path.assert_called_once_with('/valid/file.txt')
            mock_file.assert_called_once_with(mock_file_path, "r", encoding='utf-8')
            mock_print.assert_called_once_with(mock_file_content)

    @patch('src.sub_functions.cat_dependences.Path')
    def test_cat_realisation_file_not_found(self, mock_path):
        """Тест cat_realisation с несуществующим файлом - должен выбросить FileNotFoundError"""
        # Настраиваем мок Path
        mock_file_path = MagicMock()
        mock_path.return_value = mock_file_path

        # Мокаем открытие файла чтобы выбросить FileNotFoundError
        with patch('builtins.open', side_effect=FileNotFoundError("File not found")):
            with self.assertRaises(FileNotFoundError):
                cat_realisation('/nonexistent/file.txt')

    @patch('src.sub_functions.cat_dependences.Path')
    def test_cat_realisation_permission_error(self, mock_path):
        """Тест cat_realisation с файлом без прав доступа - должен выбросить PermissionError"""
        # Настраиваем мок Path
        mock_file_path = MagicMock()
        mock_path.return_value = mock_file_path

        # Мокаем открытие файла чтобы выбросить PermissionError
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with self.assertRaises(PermissionError):
                cat_realisation('/restricted/file.txt')

    @patch('src.sub_functions.cat_dependences.Path')
    def test_cat_realisation_unicode_error(self, mock_path):
        """Тест cat_realisation с файлом в неправильной кодировке - должен выбросить UnicodeError"""
        # Настраиваем мок Path
        mock_file_path = MagicMock()
        mock_path.return_value = mock_file_path

        # Мокаем открытие файла чтобы выбросить UnicodeDecodeError
        with patch('builtins.open', side_effect=UnicodeDecodeError('utf-8', b'\x00', 0, 1, 'invalid start byte')):
            with self.assertRaises(UnicodeDecodeError):
                cat_realisation('/invalid/encoding/file.txt')

    @patch('src.sub_functions.cat_dependences.print')
    @patch('src.sub_functions.cat_dependences.Path')
    def test_cat_realisation_empty_file(self, mock_path, mock_print):
        """Тест cat_realisation с пустым файлом - успешный случай"""
        # Настраиваем мок Path
        mock_file_path = MagicMock()
        mock_path.return_value = mock_file_path

        # Мокаем открытие пустого файла
        with patch('builtins.open', mock_open(read_data="")):
            # Вызов функции - не должно быть исключений
            cat_realisation('/empty/file.txt')

            # Проверяем вызовы
            mock_path.assert_called_once_with('/empty/file.txt')
            mock_print.assert_called_once_with("")

    @patch('src.sub_functions.cat_dependences.print')
    @patch('src.sub_functions.cat_dependences.Path')
    def test_cat_realisation_large_file(self, mock_path, mock_print):
        """Тест cat_realisation с большим файлом - успешный случай"""
        # Настраиваем мок Path
        mock_file_path = MagicMock()
        mock_path.return_value = mock_file_path

        # Создаем большое содержимое файла
        large_content = "Line " + "x" * 1000 + "\n"
        large_content = large_content * 100  # 100 строк по 1000+ символов

        # Мокаем открытие файла с большим содержимым
        with patch('builtins.open', mock_open(read_data=large_content)):
            # Вызов функции - не должно быть исключений
            cat_realisation('/large/file.txt')

            # Проверяем вызовы
            mock_path.assert_called_once_with('/large/file.txt')
            mock_print.assert_called_once_with(large_content)

    @patch('src.sub_functions.cat_dependences.print')
    @patch('src.sub_functions.cat_dependences.Path')
    def test_cat_realisation_multiline_file(self, mock_path, mock_print):
        """Тест cat_realisation с многострочным файлом - успешный случай"""
        # Настраиваем мок Path
        mock_file_path = MagicMock()
        mock_path.return_value = mock_file_path

        # Многострочное содержимое
        multiline_content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"

        # Мокаем открытие файла с многострочным содержимым
        with patch('builtins.open', mock_open(read_data=multiline_content)):
            # Вызов функции - не должно быть исключений
            cat_realisation('/multiline/file.txt')

            # Проверяем вызовы
            mock_path.assert_called_once_with('/multiline/file.txt')
            mock_print.assert_called_once_with(multiline_content)


class TestCatIntegration(unittest.TestCase):
    """Интеграционные тесты для команды cat"""

    @patch('src.sub_functions.cat_dependences.print')
    @patch('src.sub_functions.cat_dependences.Path')
    def test_cat_args_parse_then_realisation(self, mock_path, mock_print):
        """Тест последовательности: cat_args_parse затем cat_realisation"""
        # Настраиваем мок Path для cat_args_parse
        mock_file_path = MagicMock()
        mock_file_path.exists.return_value = True
        mock_file_path.is_dir.return_value = False
        mock_file_path.is_symlink.return_value = False
        mock_path.return_value = mock_file_path

        # Парсим аргументы
        result_path = cat_args_parse(['/test/file.txt'])

        # Проверяем что вернулся правильный путь
        self.assertEqual(result_path, mock_file_path)

        # Мокаем открытие файла для cat_realisation
        test_content = "Test file content"
        with patch('builtins.open', mock_open(read_data=test_content)):
            # Выполняем cat_realisation
            cat_realisation('/test/file.txt')

            # Проверяем вызовы
            mock_print.assert_called_once_with(test_content)


if __name__ == '__main__':
    unittest.main()
