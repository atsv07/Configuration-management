@echo off
REM Проверка: если VFS не существует, эмулятор должен её создать.

python "%~dp0..\main.py" --vfs "%~dp0..\vfs_new"

pause