import time

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout

from components.Q2AudioDataTreeWidget import Q2AudioDataTreeWidget
from components.Q2AudioPlayerWidget import Q2AudioPlayerWidget
from components.Q2FileDialog import Q2FileDialog
from components.Q2MetadataManager import Q2MetadataManager
from components.Q2TrackEditDialog import Q2TrackEditDialog


class Q2MainApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.resize(800, 600)
        self.setWindowTitle("Custom Music Player 3")

        self.metadata_manager = Q2MetadataManager(None)
        self.audio_player = Q2AudioPlayerWidget(None, self.metadata_manager)
        self.audio_data_tree = Q2AudioDataTreeWidget(None, self.metadata_manager)
        self.track_edit_dialog = Q2TrackEditDialog(self, self.metadata_manager)
        self.file_dialog = Q2FileDialog(self, "Open WAVE file", "WAVE File (*.wav)")

        self.app_main_widget = QWidget()
        self.setCentralWidget(self.app_main_widget)
        self.app_main_widget.setLayout(QHBoxLayout())

        self.app_info_widget = QWidget()

        self.app_main_widget.layout().addWidget(self.audio_player)
        self.app_main_widget.layout().addWidget(self.app_info_widget)

        self.app_info_widget.setLayout(QVBoxLayout())
        self.app_info_widget.layout().addWidget(self.metadata_manager)
        self.app_info_widget.layout().addWidget(self.audio_data_tree)

        self.metadata_manager.add_new_song_requested.connect(self.file_dialog.open)
        self.metadata_manager.new_edit_requested.connect(self.track_edit_dialog.open_new)

        self.audio_data_tree.play_track_requested.connect(self.audio_player.play_track_from_tree)
        self.audio_data_tree.play_song_requested.connect(self.audio_player.play_song_from_tree)
        self.audio_data_tree.edit_requested.connect(self.track_edit_dialog.open_new)
        self.audio_data_tree.add_track_requested.connect(self.metadata_manager.add_track)

        self.file_dialog.fileSelected.connect(self.metadata_manager.new_file_added)
        self.track_edit_dialog.edit_submitted.connect(self.metadata_manager.update_track)

    @Slot()
    def about_to_quit(self):
        self.audio_player.stop_thread()
        time.sleep(0.2)
