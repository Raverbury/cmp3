import PySide6
from PySide6.QtCore import Slot, QPoint, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu

from components.Q2MetadataManager import Q2MetadataManager


class Q2AudioDataTreeWidget(QTreeWidget):

    played = Signal(str, str)

    def __init__(self, parent: PySide6.QtWidgets.QWidget, metadata_manager: Q2MetadataManager):
        super().__init__(parent=parent)

        self.__metadata_manager = metadata_manager
        self.action_remove_track = QAction(text="Remove", parent=self)
        self.action_play_track = QAction(text="Play", parent=self)

        self.setContextMenuPolicy(PySide6.QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._custom_context_menu_requested)
        self.setColumnCount(3)
        self.setHeaderLabels(["Track", "Loop start", "Loop end"])
        self.render_tree(self.__metadata_manager.metadata_object)

        self.__metadata_manager.metadata_changed.connect(self.render_tree)
        self.action_remove_track.triggered.connect(self.action_remove_track_triggered)
        self.action_play_track.triggered.connect(self.action_remove_play_triggered)

    @Slot(QPoint)
    def _custom_context_menu_requested(self, q_point):
        menu = QMenu()
        item = self.itemAt(q_point)
        if item is None:
            return

        if item.parent() is None:
            return

        menu.addAction(self.action_remove_track)
        menu.addAction(self.action_play_track)
        self.action_remove_track.setData([item.parent().data(0, 0), item.data(0, 0)])
        self.action_play_track.setData([item.parent().data(0, 0), item.data(0, 0)])
        menu.exec(self.mapToGlobal(q_point))

    @Slot(bool)
    def action_remove_track_triggered(self, arg):
        lst = self.action_remove_track.data()
        file_path = lst[0]
        track_name = lst[1]
        self.__metadata_manager.remove_track(file_path, track_name)

    @Slot(bool)
    def action_remove_play_triggered(self, arg):
        lst = self.action_play_track.data()
        file_path = lst[0]
        track_name = lst[1]
        self.played.emit(file_path, track_name)

    def render_tree(self, audio_data):
        items = []
        for file_path, tracks in audio_data.items():
            item = QTreeWidgetItem([file_path])
            for track_name, loop_time in tracks.items():
                inner_item: QTreeWidgetItem = QTreeWidgetItem([track_name] + loop_time)
                item.addChild(inner_item)
            items.append(item)

        self.clear()
        self.insertTopLevelItems(0, items)
        self.expandAll()
