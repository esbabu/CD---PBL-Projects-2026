import sys
import os
import traceback
from pathlib import Path

# Ensure the root project directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.gui.theme import MAIN_STYLESHEET


def _install_exception_logger():
    """Write unexpected main-thread exceptions to logs/app_crash.log."""
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        try:
            log_dir = Path(__file__).resolve().parent / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            with (log_dir / "app_crash.log").open("a", encoding="utf-8") as handle:
                handle.write("\n===== UNHANDLED APPLICATION EXCEPTION =====\n")
                traceback.print_exception(exc_type, exc_value, exc_traceback, file=handle)
        except Exception:
            pass
        # Do not delegate an uncaught Qt-slot exception to PyQt's default
        # hook: some PyQt configurations abort the whole process. Keep the
        # window alive and preserve the traceback in logs/app_crash.log.
        try:
            sys.__stderr__.write(
                f"Application exception (logged to logs/app_crash.log): {exc_value}\n"
            )
            sys.__stderr__.flush()
        except Exception:
            pass

    sys.excepthook = handle_exception


def main():
    _install_exception_logger()
    app = QApplication(sys.argv)
    app.setStyleSheet(MAIN_STYLESHEET)
    
    window = MainWindow()
    window.resize(1280, 850)
    window.setMinimumSize(1050, 700)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()


