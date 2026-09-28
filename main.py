import os
import sys
import getpass
import socket
import re

def get_prompt():
    try:
        username = getpass.getuser()
    except Exception:
        username = "unknown_user"
    
    hostname = socket.gethostname()
    
    # 1. Сначала получаем текущую директорию
    cwd = os.getcwd()
    
    # 2. Потом работаем с ней
    home = os.path.expanduser("~")
    if cwd.startswith(home):
        cwd = cwd.replace(home, "~", 1)
        
    return f"{username}@{hostname}:{cwd}$ "

def expand_variables(args):
    expanded_args = []
    for arg in args:
        def replacer(match):
            var_name = match.group(1) or match.group(2)
            return os.environ.get(var_name, '')
        expanded_arg = re.sub(r'\$\{(\w+)\}|\$(\w+)', replacer, arg)
        expanded_args.append(expanded_arg)
    return expanded_args

def cmd_ls(args):
    print(f"ls: работает. Аргумент: {args}")

def cmd_cd(args):
    print(f"cd: работает. Аргумент: {args}")

def cmd_exit(args):
    print("Выход")
    sys.exit(0)

COMMANDS = {"ls": cmd_ls, "cd": cmd_cd, "exit": cmd_exit}

def main():
    while True:
        try:
            prompt = get_prompt()
            user_input = input(prompt)
            
            if not user_input.strip():
                continue
                
            parts = user_input.split()
            command = parts[0]
            args = parts[1:]

            args = expand_variables(args)

            if command in COMMANDS:
                COMMANDS[command](args)
            else:
                print(f"{command}: команда не найдена", file=sys.stderr)   
        except KeyboardInterrupt:
            print("\nДля выхода введите 'exit' ")
        except EOFError:
            print("\nВыход.")
            break
        except Exception as e:
            print(f"Ошибка: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()