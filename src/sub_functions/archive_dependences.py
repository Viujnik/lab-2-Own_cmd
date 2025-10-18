import logging
import shutil
from pathlib import Path


# Здесь собраны функции, необходимые основной функции - archive, чтобы не загрязнять и так грязный main

def archive_args_parse(args: list[str]) -> list[str]:
    if len(args) != 3:
        error_msg = f"Ожидается 3 аргумента (cmd, path_from, archive_name), передано {len(args)}."
        logging.error(error_msg)
        raise ValueError(error_msg)

    cmd, path_from, archive_name = args

    # Проверка существования директории
    if not Path(path_from).is_dir():
        error_msg = f"Директория {path_from} не найдена"
        logging.error(error_msg)
        raise FileNotFoundError(error_msg)

    # Проверка расширений архивов
    if cmd == "zip":
        if not archive_name.endswith(".zip"):
            error_msg = "Неверное имя архива. Для типа zip используйте расширение .zip"
            logging.error(error_msg)
            raise ValueError(error_msg)
    elif cmd == "tar":
        if not archive_name.endswith(".tar.gz"):
            error_msg = "Неверное имя архива. Для типа tar используйте расширение .tar.gz"
            logging.error(error_msg)
            raise ValueError(error_msg)
    else:
        error_msg = f"Поддерживаются только команды 'zip' и 'tar', получено: {cmd}"
        logging.error(error_msg)
        raise ValueError(error_msg)

    return args


def archive_realisation(args: list[str]) -> None:
    cmd, path_from, archive_name = args
    try:
        # Создаем архив в той же директории, что и path_from
        source_dir = Path(path_from)
        archive_path = source_dir.parent / archive_name

        # Убираем расширение для корректной работы make_archive
        archive_base = str(archive_path.with_suffix(''))

        if cmd == "zip":
            shutil.make_archive(archive_base, "zip", path_from)
        else:
            shutil.make_archive(archive_base, "gztar", path_from)

    except Exception as e:
        logging.error(f"Ошибка при создании архива: {str(e)}")
        raise
