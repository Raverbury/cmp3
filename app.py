import sys

from PySide6.QtWidgets import QApplication

from components.Q2MainApp import Q2MainApp


def main():
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    main_app = Q2MainApp()
    app.aboutToQuit.connect(main_app.about_to_quit)
    main_app.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
