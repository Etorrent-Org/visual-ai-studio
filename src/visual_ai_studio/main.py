from __future__ import annotations

import sys
from importlib.resources import files

from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from visual_ai_studio.application import build_application
from visual_ai_studio.ui.main_window import MainWindow


def main() -> int:
    QCoreApplication.setApplicationName("Visual AI Studio")
    QCoreApplication.setOrganizationName("Visual AI Studio")
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setWindowIcon(
        QIcon(str(files("visual_ai_studio.resources").joinpath("visual-ai-studio.ico")))
    )
    app.setStyle("Fusion")
    app.setStyleSheet(
        files("visual_ai_studio.resources").joinpath("styles.qss").read_text(encoding="utf-8")
    )
    context = build_application()
    window = MainWindow(context)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
