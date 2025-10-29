import os
import sys
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import zipfile
import tarfile
from src.sub_functions.archive_dependences import archive_args_parse, archive_realisation
from src.sub_functions.unarchive_dependences import unarchive_args_parse, unarchive_realisation

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


class TestArchiveCommands(unittest.TestCase):

    def setUp(self):
        """Создает временную директорию для каждого теста."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """Удаляет временную директорию после каждого теста."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @staticmethod
    def _create_test_files(directory, num_files=3):
        """Создает тестовые файлы в указанной директории."""
        for i in range(num_files):
            test_file = os.path.join(directory, f'test_file_{i}.txt')
            with open(test_file, 'w') as f:
                f.write(f'Test content {i}')

    def test_archive_args_parse_valid_zip(self):
        """Тест парсинга валидных аргументов для ZIP архива."""
        args = ['zip', self.test_dir, 'archive.zip']
        result = archive_args_parse(args)
        self.assertEqual(result[0], 'zip')
        self.assertEqual(str(result[1]), self.test_dir)
        self.assertEqual(result[2], 'archive.zip')
        self.assertIsInstance(result, list)

    def test_archive_args_parse_valid_tar(self):
        """Тест парсинга валидных аргументов для TAR архива."""
        args = ['tar', self.test_dir, 'archive.tar.gz']
        result = archive_args_parse(args)
        self.assertEqual(result[0], 'tar')
        self.assertEqual(str(result[1]), self.test_dir)
        self.assertEqual(result[2], 'archive.tar.gz')
        self.assertIsInstance(result, list)

    def test_archive_args_parse_zip_wrong_extension(self):
        """Тест парсинга аргументов для ZIP с неправильным расширением."""
        args = ['zip', self.test_dir, 'archive.tar']
        with self.assertRaises(ValueError):
            archive_args_parse(args)

    def test_archive_args_parse_tar_wrong_extension(self):
        """Тест парсинга аргументов для TAR с неправильным расширением."""
        args = ['tar', self.test_dir, 'archive.zip']
        with self.assertRaises(ValueError):
            archive_args_parse(args)

    def test_archive_args_parse_excessive_args(self):
        """Тест парсинга с избыточным количеством аргументов."""
        args = ['zip', self.test_dir, 'archive.zip', 'extra_arg']
        with self.assertRaises(ValueError):
            archive_args_parse(args)

    def test_archive_args_parse_insufficient_args(self):
        """Тест парсинга с недостаточным количеством аргументов."""
        args = ['zip', self.test_dir]
        with self.assertRaises(ValueError):
            archive_args_parse(args)

    def test_archive_args_parse_nonexistent_directory(self):
        """Тест парсинга с несуществующей директорией."""
        args = ['zip', '/nonexistent/directory', 'archive.zip']
        with self.assertRaises(FileNotFoundError):
            archive_args_parse(args)

    def test_archive_realisation_zip_success(self):
        """Тест успешного создания ZIP архива с реальными файлами."""
        self._create_test_files(self.test_dir, 3)
        args = ['zip', self.test_dir, 'test_archive.zip']
        archive_realisation(args)
        archive_path = os.path.join(self.test_dir, 'test_archive.zip')
        self.assertTrue(os.path.exists(archive_path))
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            file_list = zipf.namelist()
            expected_files = [f'test_file_{i}.txt' for i in range(3)]
            for expected_file in expected_files:
                self.assertIn(expected_file, file_list)

    def test_archive_realisation_tar_success(self):
        """Тест успешного создания TAR.GZ архива с реальными файлами."""
        self._create_test_files(self.test_dir, 2)
        args = ['tar', self.test_dir, 'test_archive.tar.gz']
        archive_realisation(args)
        archive_path = os.path.join(self.test_dir, 'test_archive.tar.gz')
        self.assertTrue(os.path.exists(archive_path))

    def test_archive_realisation_different_parent_directory(self):
        """Создание архива в директории, отличной от исходной."""
        archive_dir = tempfile.mkdtemp()
        try:
            self._create_test_files(self.test_dir, 2)
            archive_path = os.path.join(archive_dir, 'external_archive.tar.gz')
            args = ['tar', self.test_dir, archive_path]
            archive_realisation(args)
            self.assertTrue(os.path.exists(archive_path))
        finally:
            import shutil
            shutil.rmtree(archive_dir, ignore_errors=True)

    def test_archive_realisation_relative_path(self):
        """Тест создания архива с относительным путем."""
        subdir = os.path.join(self.test_dir, 'subdir')
        os.makedirs(subdir)
        self._create_test_files(subdir, 2)
        args = ['zip', subdir, '../relative_archive.zip']
        archive_realisation(args)
        archive_path = os.path.join(self.test_dir, 'relative_archive.zip')
        self.assertTrue(os.path.exists(archive_path))

    def test_archive_realisation_exception_handling(self):
        """Тест обработки исключений при создании архива."""
        args = ['zip', '/nonexistent/directory', 'archive.zip']
        with self.assertRaises(FileNotFoundError):
            archive_realisation(args)


class TestUnarchiveCommands(unittest.TestCase):
    """Тесты для команд разархивации: unzip и untar"""

    def setUp(self):
        """Создает временную директорию для каждого теста."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """Удаляет временную директорию после каждого теста."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_test_archive(self, archive_name, content_files=2):
        """Создает тестовый архив с файлами в текущей директории."""
        temp_files = []
        for i in range(content_files):
            temp_file = os.path.join(self.test_dir, f'test_file_{i}.txt')
            with open(temp_file, 'w') as f:
                f.write(f'Test content {i}')
            temp_files.append(temp_file)

        archive_path = os.path.join(self.test_dir, archive_name)
        if archive_name.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'w') as zipf:
                for file_path in temp_files:
                    zipf.write(file_path, os.path.basename(file_path))
        elif archive_name.endswith('.tar.gz'):
            with tarfile.open(archive_path, 'w:gz') as tarf:
                for file_path in temp_files:
                    tarf.add(file_path, arcname=os.path.basename(file_path))

        for file_path in temp_files:
            os.remove(file_path)

        return archive_name

    def test_unarchive_args_parse_valid_unzip(self):
        """Тест парсинга валидных аргументов для UNZIP."""
        archive_name = self._create_test_archive('test.zip')
        args = ['unzip', archive_name]
        result = unarchive_args_parse(args)
        self.assertEqual(result[0], 'unzip')
        self.assertEqual(result[1], archive_name)
        self.assertEqual(result[2], 'zip')
        self.assertEqual(result[3], 'test')
        self.assertIsInstance(result, list)

    def test_unarchive_args_parse_valid_untar(self):
        """Тест парсинга валидных аргументов для UNTAR."""
        archive_name = self._create_test_archive('test.tar.gz')
        args = ['untar', archive_name]
        result = unarchive_args_parse(args)
        self.assertEqual(result[0], 'untar')
        self.assertEqual(result[1], archive_name)
        self.assertEqual(result[2], 'gztar')
        self.assertEqual(result[3], 'test')
        self.assertIsInstance(result, list)

    def test_unarchive_args_parse_insufficient_args(self):
        """Тест парсинга с недостаточным количеством аргументов."""
        args = ['unzip']
        with self.assertRaises(ValueError) as context:
            unarchive_args_parse(args)
        self.assertIn("Ожидается 2 аргумента", str(context.exception))

    def test_unarchive_args_parse_excessive_args(self):
        """Тест парсинга с избыточным количеством аргументов."""
        args = ['unzip', 'test.zip', 'extra_arg']
        with self.assertRaises(ValueError) as context:
            unarchive_args_parse(args)
        self.assertIn("Ожидается 2 аргумента", str(context.exception))

    def test_unarchive_args_parse_nonexistent_archive(self):
        """Тест парсинга с несуществующим архивом."""
        args = ['unzip', 'nonexistent.zip']
        with self.assertRaises(FileNotFoundError) as context:
            unarchive_args_parse(args)
        self.assertIn("Архив nonexistent.zip не существует", str(context.exception))

    def test_unarchive_args_parse_directory_instead_of_file(self):
        """Тест парсинга с директорией вместо файла архива."""
        args = ['unzip', self.test_dir]
        with self.assertRaises(FileNotFoundError) as context:
            unarchive_args_parse(args)
        self.assertIn(f"Архив {self.test_dir} не существует", str(context.exception))

    def test_unarchive_args_parse_unsupported_format(self):
        """Тест парсинга с неподдерживаемым форматом архива."""
        test_file = os.path.join(self.test_dir, 'test.rar')
        with open(test_file, 'w') as f:
            f.write('fake archive content')
        args = ['unzip', 'test.rar']
        with self.assertRaises(ValueError) as context:
            unarchive_args_parse(args)
        self.assertIn("Неподдерживаемый формат архива", str(context.exception))

    def test_unarchive_args_parse_cmd_format_mismatch_unzip(self):
        """Тест несоответствия команды unzip и формата архива."""
        archive_name = self._create_test_archive('test.tar.gz')
        args = ['unzip', archive_name]
        with self.assertRaises(ValueError) as context:
            unarchive_args_parse(args)
        self.assertIn("Команда unzip ожидает архив с расширением .zip", str(context.exception))

    def test_unarchive_args_parse_cmd_format_mismatch_untar(self):
        """Тест несоответствия команды untar и формата архива."""
        archive_name = self._create_test_archive('test.zip')
        args = ['untar', archive_name]
        with self.assertRaises(ValueError) as context:
            unarchive_args_parse(args)
        self.assertIn("Команда untar ожидает архив с расширением .tar.gz", str(context.exception))

    def test_unarchive_args_parse_tar_stem_calculation(self):
        """Тест правильности вычисления имени папки для tar.gz архивов."""
        archive_name = self._create_test_archive('complex.name.tar.gz')
        args = ['untar', archive_name]
        result = unarchive_args_parse(args)
        self.assertEqual(result[3], 'complex.name')
        self.assertIsInstance(result, list)

    @patch('src.sub_functions.unarchive_dependences.shutil.unpack_archive')
    @patch('src.sub_functions.unarchive_dependences.zipfile.ZipFile')
    def test_unarchive_realisation_unzip_success(self, mock_zipfile, _mock_unpack):
        """Тест успешной разархивации ZIP архива."""
        mock_zip_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
        mock_zip_instance.testzip.return_value = None
        args = ['unzip', 'test.zip', 'zip', 'test']
        unarchive_realisation(args)
        mock_zipfile.assert_called_once_with('test.zip', 'r')

    @patch('src.sub_functions.unarchive_dependences.shutil.unpack_archive')
    @patch('src.sub_functions.unarchive_dependences.tarfile.open')
    def test_unarchive_realisation_untar_success(self, mock_tarfile, _mock_unpack):
        """Тест успешной разархивации TAR.GZ архива."""
        mock_tar_instance = MagicMock()
        mock_tarfile.return_value.__enter__.return_value = mock_tar_instance
        args = ['untar', 'test.tar.gz', 'gztar', 'test']
        unarchive_realisation(args)
        mock_tarfile.assert_called_once_with('test.tar.gz', 'r:gz')

    @patch('src.sub_functions.unarchive_dependences.shutil.unpack_archive')
    @patch('src.sub_functions.unarchive_dependences.zipfile.ZipFile')
    def test_unarchive_realisation_broken_zip_archive(self, mock_zipfile, _mock_unpack):
        """Тест обработки битого ZIP архива."""
        mock_zip_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
        mock_zip_instance.testzip.return_value = 'broken_file.txt'
        args = ['unzip', 'broken.zip', 'zip', 'broken']
        with self.assertRaises(ValueError) as context:
            unarchive_realisation(args)
        self.assertIn("Архив broken.zip поврежден", str(context.exception))

    @patch('src.sub_functions.unarchive_dependences.shutil.unpack_archive')
    @patch('src.sub_functions.unarchive_dependences.tarfile.open')
    def test_unarchive_realisation_broken_tar_archive(self, mock_tarfile, _mock_unpack):
        """Тест обработки битого TAR.GZ архива."""
        mock_tarfile.side_effect = tarfile.ReadError("Invalid tar archive")
        args = ['untar', 'broken.tar.gz', 'gztar', 'broken']
        with self.assertRaises(ValueError) as context:
            unarchive_realisation(args)
        self.assertIn("Файл broken.tar.gz не является валидным TAR.GZ-архивом", str(context.exception))

    @patch('src.sub_functions.unarchive_dependences.shutil.unpack_archive')
    @patch('src.sub_functions.unarchive_dependences.zipfile.ZipFile')
    def test_unarchive_realisation_zip_bad_zipfile(self, mock_zipfile, _mock_unpack):
        """Тест обработки невалидного ZIP файла."""
        mock_zipfile.side_effect = zipfile.BadZipFile("Not a zip file")
        args = ['unzip', 'not_zip.zip', 'zip', 'not_zip']
        with self.assertRaises(ValueError) as context:
            unarchive_realisation(args)
        self.assertIn("Файл not_zip.zip не является валидным ZIP-архивом", str(context.exception))

    @patch('src.sub_functions.unarchive_dependences.Path.mkdir')
    @patch('src.sub_functions.unarchive_dependences.shutil.unpack_archive')
    @patch('src.sub_functions.unarchive_dependences.zipfile.ZipFile')
    def test_unarchive_realisation_directory_creation(self, mock_zipfile, _mock_unpack, mock_mkdir):
        """Тест создания директории для распаковки."""
        mock_zip_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
        mock_zip_instance.testzip.return_value = None
        args = ['unzip', 'test.zip', 'zip', 'test']
        unarchive_realisation(args)
        mock_mkdir.assert_called_once_with(exist_ok=True)

    @patch('src.sub_functions.unarchive_dependences.shutil.unpack_archive')
    @patch('src.sub_functions.unarchive_dependences.zipfile.ZipFile')
    def test_unarchive_realisation_exception_propagation(self, mock_zipfile, mock_unpack):
        """Тест пробрасывания исключений из unarchive_realisation."""
        mock_zip_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
        mock_zip_instance.testzip.return_value = None
        mock_unpack.side_effect = Exception("Unexpected error during unpacking")
        args = ['unzip', 'test.zip', 'zip', 'test']
        with self.assertRaises(Exception) as context:
            unarchive_realisation(args)
        self.assertEqual(str(context.exception), "Unexpected error during unpacking")


if __name__ == '__main__':
    unittest.main()
