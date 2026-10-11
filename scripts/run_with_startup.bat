@echo off
REM Запуск эмулятора с VFS и стартовым скриптом.

python "%~dp0..\main.py" ^
    --vfs "%~dp0..\vfs" ^
    --script "%~dp0startup.txt"

pause