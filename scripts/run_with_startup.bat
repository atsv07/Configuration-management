@echo off

python "%~dp0..\main.py" ^
    --vfs "%~dp0..\vfs" ^
    --script "%~dp0startup.txt"

pause