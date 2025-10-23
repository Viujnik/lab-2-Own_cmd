# Здесь собраны функции, необходимые основным функциям - unzip\untar, чтобы не загрязнять и так грязный main
import logging
import shutil
import zipfile
import tarfile
from pathlib import Path


def unarchive_args_parse(args: list[str]) -> list[str]:
    if len(args) != 2:
        error_msg = f"Ожидается 2 аргумента (cmd, archive_name), передано {len(args)}."
        logging.error(error_msg)
        raise ValueError(error_msg)

    cmd, arch_name = args

    # Проверяем, что архив существует (это файл, а не директория)
    if not Path(arch_name).is_file():
        error_msg = f"Архив {arch_name} не существует."
        logging.error(error_msg)
        raise FileNotFoundError(error_msg)

    # Определяем формат архива на основе расширения
    if arch_name.endswith('.zip'):
        detected_format = 'zip'
    elif arch_name.endswith('.tar.gz'):
        detected_format = 'gztar'
    else:
        error_msg = f"Неподдерживаемый формат архива: {arch_name}. Поддерживаются .zip и .tar.gz"
        logging.error(error_msg)
        raise ValueError(error_msg)

    # Проверяем соответствие команды и формата архива
    if cmd == "unzip" and detected_format != 'zip':
        error_msg = f"Команда unzip ожидает архив с расширением .zip, получен: {arch_name}"
        logging.error(error_msg)
        raise ValueError(error_msg)

    if cmd == "untar" and detected_format != 'gztar':
        error_msg = f"Команда untar ожидает архив с расширением .tar.gz, получен: {arch_name}"
        logging.error(error_msg)
        raise ValueError(error_msg)

    # Создаем имя папки для распаковки (без расширения)
    archive_stem = Path(arch_name).stem
    # Для tar.gz нужно убрать еще .tar из имени
    if detected_format == 'gztar' and archive_stem.endswith('.tar'):
        archive_stem = archive_stem[:-4]  # Убираем .tar

    return [cmd, arch_name, detected_format, archive_stem]


def unarchive_realisation(args: list[str]) -> None:
    cmd, arch_name, archive_format, extract_dir_name = args
    try:
        # Проверяем, является ли файл валидным архивом
        if archive_format == 'zip':
            try:
                with zipfile.ZipFile(arch_name, 'r') as zip_ref:
                    # Простая проверка целостности архива
                    bad_file = zip_ref.testzip()
                    if bad_file is not None:
                        error_msg = f"Архив {arch_name} поврежден. Первый поврежденный файл: {bad_file}"
                        logging.error(error_msg)
                        raise ValueError(error_msg)
            except zipfile.BadZipFile:
                error_msg = f"Файл {arch_name} не является валидным ZIP-архивом"
                logging.error(error_msg)
                raise ValueError(error_msg)
        else:  # archive_format == 'gztar'
            try:
                with tarfile.open(arch_name, 'r:gz') as tar_ref:
                    # Простая проверка целостности архива
                    tar_ref.getmembers()
            except tarfile.ReadError:
                error_msg = f"Файл {arch_name} не является валидным TAR.GZ-архивом"
                logging.error(error_msg)
                raise ValueError(error_msg)

        # Создаем папку для распаковки
        extract_path = Path(".") / extract_dir_name
        extract_path.mkdir(exist_ok=True)

        # Распаковываем архив в созданную папку
        shutil.unpack_archive(arch_name, extract_path, archive_format)

    except Exception as e:
        logging.error(f"Ошибка при распаковке архива: {e}")
        raise e
