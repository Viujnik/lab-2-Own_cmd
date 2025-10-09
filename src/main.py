from ls_sub_functions.ls_dependence import *

app = typer.Typer()


@app.command()
def ls(func_name: str, path: str = typer.Argument(None),
       long: bool = typer.Option(False, "-l", "--long", help="Подробный вывод")):
    """Вывод файлов/директорий"""
    if func_name == "ls":
        try:
            if path:
                list_path = Path(path)
            else:
                list_path = Path.cwd()
            if not list_path.exists():
                typer.echo(f"ls: Нет такого файла/директории, {list_path}")
                raise typer.Exit(1)
            files_in_dir = []
            for dir_file in list_path.iterdir():
                if dir_file.name.startswith("."):
                    continue
                files_in_dir.append(dir_file)
            files_in_dir.sort(key=lambda x: x.name, reverse=False)
            if long:
                detailed_list(files_in_dir)
            else:
                for dir_file in files_in_dir:
                    if dir_file.is_dir():
                        typer.echo(typer.style(f"{dir_file.name}/", fg=typer.colors.BLUE))
                    elif dir_file.is_symlink():
                        typer.echo(typer.style(f"{dir_file.name}@", fg=typer.colors.CYAN))
                    elif os.access(dir_file, os.X_OK):
                        typer.echo(typer.style(f"{dir_file.name}*", fg=typer.colors.GREEN))
                    else:
                        typer.echo(dir_file.name)
        except PermissionError:
            typer.echo(f"Недостаточно прав для открытия директории {path}", err=True)
            raise typer.Exit(2)
        except Exception as e:
            typer.echo(f"Неизвестная ошибка: {e}", err=True)
            raise typer.Exit(1)

@app.command()
def cd():
    pass


if __name__ == "__main__":
    app()
