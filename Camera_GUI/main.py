# This Python file uses the following encoding: utf-8
import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QDockWidget



if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    engine.addImportPath(Path(__file__).parent)
    engine.loadFromModule("Camera_GUI", "Main")
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())

    function playClicked(){
        # stop/start stream when play button is clicked
    }
