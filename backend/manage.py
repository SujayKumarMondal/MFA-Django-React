#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable?"
        ) from exc

    # Automatically add port 8015 if 'runserver' is used without port
    if len(sys.argv) == 2 and sys.argv[1] == "runserver":
        sys.argv.append("8015")

    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
