import PySide6
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QFileDialog


class Q2FileDialog(QFileDialog):

    def __init__(self, parent: PySide6.QtWidgets.QWidget, caption_string: str, filter_string: str):
        super().__init__(parent=parent, caption=caption_string, filter=filter_string)

    @Slot(str)
    def on_file_selected(self, file_path):
        self.hide()
