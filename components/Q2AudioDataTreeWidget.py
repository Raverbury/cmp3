import PySide6
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem


class Q2AudioDataTreeWidget(QTreeWidget):

    def __init__(self, parent: PySide6.QtWidgets.QWidget):
        super().__init__(parent=parent)
        # read json from somewhere
        self.audio_data = {
            "C:\\Users": {
                "loop1": ["00.00.00:000", "00.00.05:000"],
                "loop2": ["00.00.00:000", "00.00.05:000"],
            },
            "C:\\Users\\eflos": {
                "loop1": ["00.00.00:000", "00.00.05:000"]
            }
        }
        self.setColumnCount(3)
        self.setHeaderLabels(["Track", "Loop start", "Loop end"])
        items = []
        for file_path, tracks in self.audio_data.items():
            print(file_path)
            item = QTreeWidgetItem([file_path])
            for track_name, loop_time in tracks.items():
                inner_item = QTreeWidgetItem([track_name] + loop_time)
                item.addChild(inner_item)
            items.append(item)

        self.insertTopLevelItems(0, items)
