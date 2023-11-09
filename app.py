import sys

from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QTimeEdit, QAbstractSpinBox, QVBoxLayout, \
    QGridLayout

from components.Q2AudioDataTreeWidget import Q2AudioDataTreeWidget
from components.Q2FileDialog import Q2FileDialog
from components.Q2MainApp import Q2MainApp
from components.Q2MetadataManager import Q2MetadataManager

base = None

# def what(file_path):
#     print(file_path)
#
#
# def openFileDialog():
#     fd2 = Q2FileDialog(base, "Open WAVE file", "WAVE File (*.wav)")
#     # fd = QFileDialog(base, "Open WAVE file", "", "WAVE File (*.wav)")
#     fd2.fileSelected.connect(what)
#     fd2.show()


def main():
    global base

    # app = QApplication(sys.argv)
    # base = QWidget()
    # base.resize(800, 600)
    # base.show()
    # grid = QGridLayout()
    # base.setLayout(grid)
    # # base2 = QWidget()
    # # base2.resize(800, 600)
    # # base2.show()
    # # button = QPushButton(parent=base, text="Push me")
    # # button.show()
    # # button.pressed.connect(openFileDialog)
    # # grid.addWidget(button, 0, 0, 1, 2)
    # # timeedit = QTimeEdit(parent=base)
    # # # timeedit.setDisplayFormat("hh:mm:ss:zzz")
    # # # timeedit.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
    # # # timeedit.show()
    # # # timeedit.resize(200, 100)
    # # audio_data_tree = Q2AudioDataTreeWidget(parent=base)
    # # grid.addWidget(audio_data_tree, 0, 3, 1, 1)
    # # audio_data_tree.show()
    # metadata_watcher = Q2MetadataManager(parent=base)
    # grid.addWidget(metadata_watcher, 0, 6, 1, 1)
    # metadata_watcher.show()
    app = QApplication(sys.argv)
    main_app = Q2MainApp()
    main_app.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
