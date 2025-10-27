import shutil
from pathlib import Path

# Здесь собраны функции, необходимые функции архивирования, чтобы не загрязнять и так грязный main


def archive_args_parse(args: list[str]) -> list:
    """
    Парсит аргументы для команд архивации.
    """
    if len(args) != 3:
        raise ValueError("Неверное количество аргументов. Используйте: archive <zip|tar> <директория> <имя_архива>")

    archive_type = args[0].lower()
    source_dir = args[1]
    archive_name = args[2]

    if source_dir.startswith("'") and source_dir.endswith("'"):
        source_dir = source_dir[1:-1]

    if archive_name.startswith("'") and archive_name.endswith("'"):
        archive_name = archive_name[1:-1]

    archive_name = archive_name
    source_dir_path = Path(source_dir)

    if not source_dir_path.exists():
        raise FileNotFoundError(f"Директория {source_dir_path} не найдена")

    if not source_dir_path.is_dir():
        raise ValueError(f"{source_dir_path} не является директорией")

    # Проверяем расширения архивов
    if archive_type == 'zip' and not archive_name.endswith('.zip'):
        raise ValueError("Для zip архива имя должно заканчиваться на .zip")

    if archive_type == 'tar' and not (archive_name.endswith('.tar.gz') or archive_name.endswith('.tar')):
        raise ValueError("Для tar архива имя должно заканчиваться на .tar или .tar.gz")

    return [archive_type, source_dir_path, archive_name]


def archive_realisation(args: list) -> None:
    """
    Создает архив указанного типа.
    """
    try:
        archive_type, source_dir, archive_name = archive_args_parse(args)

        if archive_type == 'zip':
            _create_zip_archive(source_dir, archive_name)
        else:  # tar
            _create_tar_archive(source_dir, archive_name)

    except Exception as e:
        raise e


def _create_zip_archive(source_dir: Path, archive_name: str) -> None:
    """Создает ZIP архив с использованием shutil.make_archive."""
    # Создаем полный путь к архиву
    archive_path = Path(archive_name)
    if not archive_path.is_absolute():
        archive_path = source_dir / archive_path

    # Создаем базовое имя без расширения .zip
    base_name = archive_path.with_suffix('')

    # Создаем родительские директории, если их нетa
    base_name.parent.mkdir(parents=True, exist_ok=True)

    shutil.make_archive(str(base_name), 'zip', source_dir)


def _create_tar_archive(source_dir: Path, archive_name: str) -> None:
    """Создает TAR архив."""
    # Определяем формат архива по расширению
    if archive_name.endswith('.tar.gz'):
        format_type = 'gztar'
    else:
        format_type = 'tar'

    # Создаем полный путь к архиву
    archive_path = Path(archive_name)
    if not archive_path.is_absolute():
        archive_path = source_dir / archive_path

    # Создаем базовое имя без расширения
    if format_type == 'gztar':
        # Для .tar.gz удаляем расширение
        base_name = archive_path.with_suffix('').with_suffix('')
    else:
        # Для .tar удаляем одно расширение
        base_name = archive_path.with_suffix('')

    # Создаем родительские директории, если их нет
    base_name.parent.mkdir(parents=True, exist_ok=True)

    shutil.make_archive(str(base_name), format_type, source_dir)
