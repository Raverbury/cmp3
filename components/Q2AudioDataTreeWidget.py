import PySide6
from PySide6.QtCore import Slot, QPoint, Signal, Qt, QUrl
from PySide6.QtGui import QAction, QMouseEvent, QKeyEvent
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QHeaderView

from components.Q2MetadataManager import Q2MetadataManager


class Q2AudioDataTreeWidget(QTreeWidget):
    play_track_requested = Signal(str, str)
    edit_requested = Signal(str, str)
    add_track_requested = Signal(str)
    play_song_requested = Signal(str)

    def __init__(self, parent: PySide6.QtWidgets.QWidget, metadata_manager: Q2MetadataManager):
        super().__init__(parent=parent)

        self.__metadata_manager = metadata_manager

        self.action_add_track = QAction(text="Add track", parent=self)
        self.action_play_song = QAction(text="Play song (default loop)", parent=self)
        self.action_remove_song = QAction(text="Remove song", parent=self)

        self.action_play_track = QAction(text="Play track", parent=self)
        self.action_edit_track = QAction(text="Edit track", parent=self)
        self.action_remove_track = QAction(text="Remove track", parent=self)

        self.setContextMenuPolicy(PySide6.QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__custom_context_menu_requested)
        self.setColumnCount(3)
        self.setHeaderLabels(["Track", "Loop start", "Loop end"])
        self.render_tree(self.__metadata_manager.metadata_object)
        self.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.header().setStretchLastSection(False)

        self.__metadata_manager.metadata_changed.connect(self.render_tree)
        self.action_add_track.triggered.connect(self.__action_add_track_triggered)
        self.action_play_song.triggered.connect(self.__action_play_song_triggered)
        self.action_remove_song.triggered.connect(self.__action_remove_song_triggered)
        self.action_play_track.triggered.connect(self.__action_play_track_triggered)
        self.action_edit_track.triggered.connect(self.__action_edit_track_triggered)
        self.action_remove_track.triggered.connect(self.__action_remove_track_triggered)

    @Slot(QPoint)
    def __custom_context_menu_requested(self, q_point):
        node_height = self.__pos_to_item_height(q_point)
        if node_height == -1:
            return
        menu = QMenu()
        if node_height == 0:
            song_item = self.itemAt(q_point)
            menu.addAction(self.action_add_track)
            menu.addAction(self.action_play_song)
            menu.addAction(self.action_remove_song)
            action_data = [song_item.data(3, 0)]
            self.action_add_track.setData(action_data)
            self.action_play_song.setData(action_data)
            self.action_remove_song.setData(action_data)
        elif node_height == 1:
            menu.addAction(self.action_play_track)
            menu.addAction(self.action_edit_track)
            menu.addAction(self.action_remove_track)
            track_item = self.itemAt(q_point)
            song_item = track_item.parent()
            action_data = [song_item.data(3, 0), track_item.data(0, 0)]
            self.action_play_track.setData(action_data)
            self.action_edit_track.setData(action_data)
            self.action_remove_track.setData(action_data)
        menu.exec(self.mapToGlobal(q_point))

    @Slot(bool)
    def __action_add_track_triggered(self, _arg):
        file_path = self.action_add_track.data()[0]
        self.add_track_requested.emit(file_path)

    @Slot(bool)
    def __action_play_song_triggered(self, _arg):
        file_path = self.action_play_song.data()[0]
        self.play_song_requested.emit(file_path)

    @Slot(bool)
    def __action_remove_song_triggered(self, _arg):
        file_path = self.action_remove_song.data()[0]
        self.__metadata_manager.remove_song(file_path)

    @Slot(bool)
    def __action_play_track_triggered(self, _arg):
        lst = self.action_play_track.data()
        file_path = lst[0]
        track_name = lst[1]
        self.play_track_requested.emit(file_path, track_name)

    @Slot(bool)
    def __action_edit_track_triggered(self, _arg):
        lst = self.action_edit_track.data()
        file_path = lst[0]
        track_name = lst[1]
        self.clearFocus()
        self.edit_requested.emit(file_path, track_name)

    @Slot(bool)
    def __action_remove_track_triggered(self, _arg):
        lst = self.action_remove_track.data()
        file_path = lst[0]
        track_name = lst[1]
        self.__metadata_manager.remove_track(file_path, track_name)

    def render_tree(self, audio_data):
        items = []
        for file_path, tracks in audio_data.items():
            q_url = QUrl(file_path)
            item = QTreeWidgetItem(["[...]" + q_url.fileName(), "", "", file_path])
            item.setToolTip(0, file_path)
            for track_name, loop_time in tracks.items():
                inner_item: QTreeWidgetItem = QTreeWidgetItem([track_name] + loop_time + ["Hello"])
                item.addChild(inner_item)
            items.append(item)

        self.clear()
        self.insertTopLevelItems(0, items)
        self.expandAll()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        event_pos = event.pos()
        node_height = self.__pos_to_item_height(event_pos)
        if node_height == -1:
            return
        if node_height == 0:
            path_item = self.itemAt(event_pos)
            file_path = path_item.data(3, 0)
            self.play_song_requested.emit(file_path)
        elif node_height == 1:
            track_item = self.itemAt(event_pos)
            path_item = track_item.parent()
            track_name = track_item.data(0, 0)
            file_path = path_item.data(3, 0)
            self.play_track_requested.emit(file_path, track_name)

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key() != Qt.Key.Key_Return.value:
            return
        items = self.selectedItems()
        if len(items) == 0:
            return
        first_item = items[0]
        node_height = self.__item_height(first_item)
        if node_height == -1:
            return
        if node_height == 0:
            path_item = first_item
            file_path = path_item.data(3, 0)
            self.play_song_requested.emit(file_path)
        elif node_height == 1:
            track_item = first_item
            path_item = track_item.parent()
            track_name = track_item.data(0, 0)
            file_path = path_item.data(3, 0)
            self.play_track_requested.emit(file_path, track_name)

    def __pos_to_item_height(self, q_point: QPoint):
        """
        Returns the height index of the item at input position relative to tree's root, 0 if root,
        1 if directly below root and so on, -1 if invalid
        @param q_point: QPoint
        @return: int
        """
        height = -1
        item = self.itemAt(q_point)
        while item is not None:
            item = item.parent()
            height += 1
        return height

    def __item_height(self, item: QTreeWidgetItem):
        """
        Returns the height index of the item at input position relative to tree's root, 0 if root,
        1 if directly below root and so on, -1 if invalid
        @param item: QTreeWidgetItem
        @return: int
        """
        height = -1
        while item is not None:
            item = item.parent()
            height += 1
        return height
