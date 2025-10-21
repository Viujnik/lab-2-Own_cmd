def help_realisation() -> None:
    """Вывод справки по командам"""
    help_text = """
Доступные команды:

ls [PATH]              - список файлов и директорий
ls -l [PATH]           - детальный список с дополнительной информацией
cd [PATH]              - смена директории
cat FILE               - вывод содержимого файла
cp SOURCE DEST         - копирование файлов/директорий
mv SOURCE DEST         - перемещение/переименование файлов/директорий
rm PATH                - удаление файлов/директорий
zip FOLDER ARCHIVE.zip - создание ZIP архива
tar FOLDER ARCHIVE.tar.gz - создание TAR.GZ архива
unzip ARCHIVE.zip      - распаковка ZIP архива
untar ARCHIVE.tar.gz   - распаковка TAR.GZ архива
grep PATTERN PATH      - поиск текста в файлах
grep -r PATTERN PATH   - рекурсивный поиск
grep -i PATTERN PATH   - поиск без учета регистра
history                - история команд
undo [N]              - отмена последних N команд
help                   - эта справка

Для получения подробной информации о команде используйте: help <command>
"""
    print(help_text)    