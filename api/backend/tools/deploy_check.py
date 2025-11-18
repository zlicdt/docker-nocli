import os
import docker
from pathlib import Path

def check_integrity() -> bool:
    # cd to the script path
    os.chdir(Path(__file__).resolve().parent)
    # Add test functions here!
    funcs_list = [
        check_originfiles,
        check_venv,
        check_docker_env,
    ]

    passed = 0
    total = len(funcs_list)
    current = 1
    
    class ANSI:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKCYAN = '\033[96m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

    for funcs in funcs_list:
        print(f"[{current}/{total}]", end=" ")
        if funcs():
            print(f"{ANSI.OKGREEN}[PASSED]{ANSI.ENDC}")
            passed += 1
        else:
            print(f"{ANSI.FAIL}[FAILED]{ANSI.ENDC}")
        current += 1
    print(f"Total: {total}, passed: {passed}, failed: {total-passed}")
    if passed == total:
        return True
    else:
        return False

def check_originfiles() -> bool:
    try:
        with open("file_lists/origin.txt", "r") as file_origin:
            file_list_origin = [line.strip() for line in file_origin]
    except:
        print("Backend integrity check failed.", end=" ")
        return False
    
    if (set(file_list_origin).issubset(set(os.listdir("..")))):
        print("Backend integrity check passed.", end=" ")
        return True
    else:
        print("Backend integrity check failed.", end=" ")
        return False

def check_venv() -> bool:
    for item in os.listdir(".."):
        if (item == ".venv"):
            print("Venv check passed(I don't know if you actually created it).", end=" ")
            return True
    print("Venv check failed.", end=" ")
    return False

def check_docker_env() -> bool:
    try:
        docker.client.from_env()
        print("Docker environment check passed.", end=" ")
        return True
    except:
        print("Docker environment check failed.", end=" ")
        return False

if __name__ == "__main__":
    check_integrity()