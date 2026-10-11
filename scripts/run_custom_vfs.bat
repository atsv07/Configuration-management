@echo off
REM Проверка работы с абсолютным путём и переменной %USERPROFILE%.

python "%~dp0..\main.py" ^
    --vfs "%USERPROFILE%\c_hw_vfs_demo" ^
    --script "%~dp0startup.txt"

pause