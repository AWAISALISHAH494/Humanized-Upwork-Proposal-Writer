import subprocess, sys

try:
    from rich.console import Console
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich==13.7.1"])
    from rich.console import Console


from app.ui.dashboard import Dashboard


def main() -> None:
    Dashboard.default().render()


if __name__ == "__main__":
    main()
