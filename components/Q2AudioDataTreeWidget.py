import PySide6
from PySide6.QtCore import Slot, QPoint
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu


class Q2AudioDataTreeWidget(QTreeWidget):

    def __init__(self, parent: PySide6.QtWidgets.QWidget):
        super().__init__(parent=parent)
        self.action_remove_track = QAction(text="Remove", parent=self)
        self.setContextMenuPolicy(PySide6.QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._custom_context_menu_requested)
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
        self.render_tree(self.audio_data)

    @Slot(QPoint)
    def _custom_context_menu_requested(self, q_point):
        menu = QMenu()
        item = self.itemAt(q_point)
        if item is None:
            return

        if item.parent() is None:
            return

        menu.addAction(self.action_remove_track)
        self.action_remove_track.setData([item.parent().data(0, 0), item.data(0, 0)])
        self.action_remove_track.triggered.connect(self.action_remove_track_triggered)
        print(self.action_remove_track.data())
        menu.exec(self.mapToGlobal(q_point))

    @Slot(bool)
    def action_remove_track_triggered(self, arg):
        lst = self.action_remove_track.data()
        file_path = lst[0]
        track_name = lst[1]
        try:
            inner_dict: dict = self.audio_data[file_path]
            inner_dict.pop(track_name)
        except KeyError:
            pass
        print(self.audio_data)
        self.render_tree(self.audio_data)

    def render_tree(self, audio_data):
        self.audio_data = audio_data
        items = []
        row_count = 0
        for file_path, tracks in self.audio_data.items():
            item = QTreeWidgetItem([file_path])
            for track_name, loop_time in tracks.items():
                inner_item: QTreeWidgetItem = QTreeWidgetItem([track_name] + loop_time)
                item.addChild(inner_item)
            items.append(item)

        self.clear()
        self.insertTopLevelItems(0, items)
        self.expandAll()
