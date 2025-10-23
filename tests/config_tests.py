"""
Конфигурация и общие утилиты для всех тестов
"""
import sys
import os
from unittest.mock import Mock
from pathlib import Path

# Добавляем src в Python path для корректных импортов
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

# Общие моки
def mock_path_basic():
    """Базовые моки для pathlib.Path"""
    mock_path = Mock(spec=Path)
    mock_path.exists.return_value = True
    mock_path.is_dir.return_value = True
    mock_path.is_file.return_value = False
    mock_path.is_symlink.return_value = False
    mock_path.name = "test_file"
    mock_path.__str__ = Mock(return_value="/test/path")
    return mock_path

def mock_os_basic():
    """Базовые моки для модуля os"""
    mock_os = Mock()
    mock_os.path.join = os.path.join
    mock_os.path.exists = Mock(return_value=True)
    mock_os.path.isdir = Mock(return_value=True)
    mock_os.path.isfile = Mock(return_value=False)
    mock_os.path.expanduser = Mock(return_value="/home/user")
    mock_os.getcwd = Mock(return_value='/test/current/dir')
    mock_os.listdir = Mock()
    mock_os.makedirs = Mock()
    mock_os.remove = Mock()
    mock_os.chdir = Mock()
    mock_os.access = Mock(return_value=True)
    mock_os.readlink = Mock(return_value="/linked/path")
    mock_os.X_OK = os.X_OK  # Передаем реальную константу
    return mock_os

def mock_stat_result():
    """Мок для stat_result"""
    mock_stat = Mock()
    mock_stat.st_mode = 0o100644  # Regular file
    mock_stat.st_nlink = 1
    mock_stat.st_uid = 1000
    mock_stat.st_gid = 1000
    mock_stat.st_size = 1024
    mock_stat.st_mtime = 1600000000.0
    return mock_stat