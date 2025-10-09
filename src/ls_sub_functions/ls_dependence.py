import os
from pathlib import Path
from datetime import datetime
import typer
import stat

# Здесь собраны функции, необходимые основной функции - ls, чтобы не загрязнять и так грязный main


def check_file_type(file):
    """Проверка файла на существование в директории/символическую ссылку"""
    if stat.S_ISDIR(file.st_mode):
        return "dir"
    elif stat.S_ISLNK(file.st_mode):
        return "lnk"
    else:
        return "unknown"


def check_access_rights(file):
    """Возвращает права доступа для файла"""
    rights = stat.filemode(file.st_mode)
    return str(rights)[-9:]


def detailed_list(files):
    """Детальный вывод для флага <-l>"""
    for file in files:
        try:
            if isinstance(file, Path):
                file_stat = file.stat()
                file_name = file.name
            else:
                file_stat = Path(file).stat()
                file_name = file
            file_type = check_file_type(file_stat)
            rights = check_access_rights(file_stat)
            links_cnt = file_stat.st_nlink
            file_uid = file_stat.st_uid
            file_gid = file_stat.st_gid
            file_size = file.stat().st_size
            mtime = datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            if stat.S_ISLNK(file_stat.st_mode):
                linked_file = os.readlink(file if isinstance(file, Path) else Path(file))
                file_name = f"{file_name} -> {linked_file}"
            typer.echo(f"{file_type}{rights} {links_cnt:>2} {file_uid} {file_gid} {file_size:>4} {mtime} {file_name}")
        except Exception as e:
            typer.echo(f"Ошибка чтения {file}: {e}", err=True)