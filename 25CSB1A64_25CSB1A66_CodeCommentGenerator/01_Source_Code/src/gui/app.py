"""GUI entry point (``python run_gui.py`` or the ``code-comment-gen-gui`` command)."""
import sys


def main() -> int:
    from src.config import APP_NAME, configure_stdio
    from PyQt6.QtWidgets import QApplication
    from src.gui.main_window import MainWindow
    from src.gui.theme import apply_theme

    configure_stdio()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    apply_theme(app)

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
