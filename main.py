#!/usr/bin/env python3
"""
Эмулятор командной оболочки UNIX-подобной ОС.
Этап 1: REPL (диалог с пользователем, парсер переменных, команды-заглушки).
Этап 2: Конфигурация (CLI-параметры + стартовый скрипт).
"""

import os
import sys
import getpass
import socket
import re
import argparse


# ---------- Приглашение ----------

def get_prompt():
    """Формирует приглашение: username@hostname:cwd$"""
    try:
        username = getpass.getuser()
    except Exception:
        username = "unknown_user"

    hostname = socket.gethostname()

    cwd = os.getcwd()
    home = os.path.expanduser("~")
    if cwd == home:
        cwd = "~"
    elif cwd.startswith(home + os.sep):
        cwd = "~" + cwd[len(home):]

    return f"{username}@{hostname}:{cwd}$ "


# ---------- Парсер переменных окружения ----------

def expand_variables(args):
    """Раскрывает $VAR и ${VAR} значениями из os.environ."""
    expanded_args = []
    for arg in args:
        def replacer(match):
            var_name = match.group(1) or match.group(2)
            return os.environ.get(var_name, '')

        expanded_arg = re.sub(r'\$\{(\w+)\}|\$(\w+)', replacer, arg)
        expanded_args.append(expanded_arg)

    return expanded_args


# ---------- Команды ----------

def cmd_ls(args, ctx):
    """Заглушка для команды ls."""
    print(f"ls: команда вызвана с аргументами: {args}")


def cmd_cd(args, ctx):
    """Заглушка для команды cd."""
    print(f"cd: команда вызвана с аргументами: {args}")


def cmd_exit(args, ctx):
    """Команда выхода из эмулятора."""
    print("Выход из эмулятора...")
    sys.exit(0)


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}


# ---------- Ядро: выполнение одной строки ----------

def execute_line(line, ctx):
    """Выполняет одну строку. Возвращает True, если команда распознана."""
    parts = line.split()
    if not parts:
        return True

    command = parts[0]
    args = parts[1:]
    args = expand_variables(args)

    if command in COMMANDS:
        try:
            COMMANDS[command](args, ctx)
        except SystemExit:
            raise
        except Exception as e:
            print(f"Ошибка выполнения '{command}': {e}", file=sys.stderr)
        return True
    else:
        print(f"{command}: команда не найдена", file=sys.stderr)
        return False


# ---------- Стартовый скрипт ----------

def run_startup_script(path, ctx):
    """
    Выполняет команды из стартового скрипта последовательно.
    Ошибочные строки пропускает.
    Отображает ввод и вывод, имитируя диалог с пользователем.
    """
    print(f"\n=== Выполнение стартового скрипта: {path} ===")

    if not os.path.isfile(path):
        print(f"Стартовый скрипт не найден: {path}", file=sys.stderr)
        return

    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Ошибка чтения скрипта: {e}", file=sys.stderr)
        return

    prompt = get_prompt()
    for line_no, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip('\n').strip()

        # Пропускаем пустые строки, shebang и комментарии
        if not line or line.startswith('#!') or line.startswith('#'):
            continue

        # Имитация диалога: приглашение + введённая строка
        print(f"{prompt}{line}")

        # Ошибка в одной строке не прерывает скрипт
        try:
            execute_line(line, ctx)
        except SystemExit:
            raise
        except Exception as e:
            print(
                f"[строка {line_no}] пропущена из-за ошибки: {e}",
                file=sys.stderr
            )

    print("=== Стартовый скрипт завершён ===\n")


# ---------- REPL ----------

def repl(ctx):
    print("Добро пожаловать в эмулятор оболочки UNIX (Этап 2).")
    print("Введите 'exit' для выхода.")

    while True:
        try:
            prompt = get_prompt()
            user_input = input(prompt)

            if not user_input.strip():
                continue

            execute_line(user_input, ctx)

        except KeyboardInterrupt:
            print("\nДля выхода введите 'exit' или нажмите Ctrl+D.")
        except EOFError:
            print("\nВыход.")
            break
        except SystemExit:
            raise
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}", file=sys.stderr)


# ---------- Аргументы командной строки ----------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Эмулятор оболочки UNIX-подобной ОС. Этап 2: конфигурация."
    )
    parser.add_argument(
        "-v", "--vfs",
        dest="vfs_path",
        required=True,
        help="Путь к физическому расположению VFS (виртуальной файловой системы)."
    )
    parser.add_argument(
        "-s", "--script",
        dest="script_path",
        default=None,
        help="Путь к стартовому скрипту (опционально)."
    )
    return parser.parse_args()


# ---------- Точка входа ----------

def main():
    # Эмуляция UNIX-переменной HOME в Windows.
    # Нужно, чтобы в стартовых скриптах работал $HOME (как в Linux).
    if "HOME" not in os.environ and "USERPROFILE" in os.environ:
        os.environ["HOME"] = os.environ["USERPROFILE"]

    args = parse_args()

    vfs_path = os.path.abspath(args.vfs_path)
    script_path = os.path.abspath(args.script_path) if args.script_path else None

    # Отладочный вывод всех заданных параметров
    print("=== Параметры запуска эмулятора ===")
    print(f"VFS path:    {vfs_path}")
    print(f"Script path: {script_path}")
    print("===================================\n")

    # VFS должна существовать как директория — создаём, если нет
    if not os.path.exists(vfs_path):
        os.makedirs(vfs_path, exist_ok=True)
        print(f"Создана директория VFS: {vfs_path}")
    elif not os.path.isdir(vfs_path):
        print(
            f"Ошибка: путь к VFS не является директорией: {vfs_path}",
            file=sys.stderr
        )
        sys.exit(1)

    ctx = {
        "vfs_path": vfs_path,
        "script_path": script_path,
    }

    # Если задан стартовый скрипт — выполняем его
    if script_path:
        try:
            run_startup_script(script_path, ctx)
        except SystemExit:
            print("Эмулятор завершён по команде из скрипта.")
            return

    # После скрипта (или если его нет) — обычный REPL
    repl(ctx)


if __name__ == "__main__":
    main()