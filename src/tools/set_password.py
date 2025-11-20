import getpass
import sys

from router import auth


def main() -> int:
    username = input("Username [admin]: ").strip() or "admin"
    password = getpass.getpass("New password: ")
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("Passwords do not match.", file=sys.stderr)
        return 1
    if not password:
        print("Password cannot be empty.", file=sys.stderr)
        return 1
    auth.upsert_credentials(username, password)
    print(f"Credentials stored for user '{username}'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
