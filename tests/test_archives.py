import os
import tempfile
import unittest
from src.sub_functions.archive_dependences import archive_args_parse, archive_realisation


class TestArchiveCommands(unittest.TestCase):

    def setUp(self):
        """Создает временную директорию для каждого теста."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Удаляет временную директорию после каждого теста."""
        import shutil
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

    def test_archive_args_parse_valid_tar(self):
        """Тест парсинга валидных аргументов для TAR архива."""
        args = ['tar', self.test_dir, 'archive.tar.gz']
        result = archive_args_parse(args)
        self.assertEqual(result[0], 'tar')
        self.assertEqual(str(result[1]), self.test_dir)
        self.assertEqual(result[2], 'archive.tar.gz')

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
        """
        Тест успешного создания ZIP архива с реальными файлами.

        Создает реальные тестовые файлы и проверяет, что архив создается
        и содержит ожидаемые файлы.
        """
        # Создаем тестовые файлы
        self._create_test_files(self.test_dir, 3)

        # Создаем архив
        args = ['zip', self.test_dir, 'test_archive.zip']
        archive_realisation(args)

        # Проверяем, что архив создан
        archive_path = os.path.join(self.test_dir, 'test_archive.zip')
        self.assertTrue(os.path.exists(archive_path))

        # Проверяем содержимое архива
        import zipfile
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            file_list = zipf.namelist()
            expected_files = [f'test_file_{i}.txt' for i in range(3)]
            for expected_file in expected_files:
                self.assertIn(expected_file, file_list)

    def test_archive_realisation_tar_success(self):
        """
        Тест успешного создания TAR.GZ архива с реальными файлами.

        Создает реальные тестовые файлы и проверяет, что архив создается.
        """
        # Создаем тестовые файлы
        self._create_test_files(self.test_dir, 2)

        # Создаем архив
        args = ['tar', self.test_dir, 'test_archive.tar.gz']
        archive_realisation(args)

        # Проверяем, что архив создан
        archive_path = os.path.join(self.test_dir, 'test_archive.tar.gz')
        self.assertTrue(os.path.exists(archive_path))

    def test_archive_realisation_different_parent_directory(self):
        """
        СЛОЖНЫЙ ТЕСТ: Создание архива в директории, отличной от исходной.

        Создает реальные файлы в одной директории и архив в другой,
        затем проверяет корректность создания.
        """
        # Создаем отдельную директорию для архива
        archive_dir = tempfile.mkdtemp()
        try:
            # Создаем тестовые файлы в исходной директории
            self._create_test_files(self.test_dir, 2)

            # Создаем архив в другой директории
            archive_path = os.path.join(archive_dir, 'external_archive.tar.gz')
            args = ['tar', self.test_dir, archive_path]
            archive_realisation(args)

            # Проверяем, что архив создан в правильной директории
            self.assertTrue(os.path.exists(archive_path))

        finally:
            import shutil
            shutil.rmtree(archive_dir, ignore_errors=True)

    def test_archive_realisation_relative_path(self):
        """
        Тест создания архива с относительным путем.

        Создает поддиректорию с файлами и архив с использованием
        относительного пути, затем проверяет результат.
        """
        # Создаем поддиректорию
        subdir = os.path.join(self.test_dir, 'subdir')
        os.makedirs(subdir)

        # Создаем файлы в поддиректории
        self._create_test_files(subdir, 2)

        # Создаем архив с относительным путем (на уровень выше)
        args = ['zip', subdir, '../relative_archive.zip']
        archive_realisation(args)

        # Проверяем, что архив создан в родительской директории
        archive_path = os.path.join(self.test_dir, 'relative_archive.zip')
        self.assertTrue(os.path.exists(archive_path))

    def test_archive_realisation_exception_handling(self):
        """
        Тест обработки исключений при создании архива.

        Проверяет, что исключения корректно пробрасываются.
        """
        # Пытаемся создать архив из несуществующей директории
        args = ['zip', '/nonexistent/directory', 'archive.zip']
        with self.assertRaises(FileNotFoundError):
            archive_realisation(args)
