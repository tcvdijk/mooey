from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap
import sys

if  __name__ == "__main__":
    # Minimal imports; show splash screen
    app = QApplication(sys.argv)
    pixmap = QPixmap("splash.png")
    splash = QSplashScreen(pixmap)
    splash.show()
    splash.raise_()
    splash.activateWindow()
    app.processEvents()

    # Now import the kitchen sink and start the app
    import mui
    window = mui.MainWindow()
    window.show()
    window.canvas.zoom_to_network()
    window.canvas.render()
    splash.finish(window)
    sys.exit(app.exec())