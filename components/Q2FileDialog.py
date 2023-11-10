import PySide6
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QFileDialog


class Q2FileDialog(QFileDialog):

    def __init__(self, parent: PySide6.QtWidgets.QWidget, caption_string: str, filter_string: str):
        super().__init__(parent=parent, caption=caption_string, filter=filter_string)

        self.setModal(True)
        self.fileSelected.connect(self.__on_file_selected)

    @Slot(str)
    def __on_file_selected(self, _file_path):
        self.close()

    @Slot()
    def open(self):
        super().open()
