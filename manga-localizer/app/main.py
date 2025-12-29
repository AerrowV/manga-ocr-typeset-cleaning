import sys
from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow

def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Manga Localizer UI")

    # Modern theme
    try:
        import qdarktheme
        app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
    except Exception:
        pass  # fallback to default

    w = MainWindow()
    w.show()
    return app.exec()
