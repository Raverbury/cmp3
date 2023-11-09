from PySide6.QtWidgets import QMainWindow, QDockWidget, QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt

from components.Q2AudioDataTreeWidget import Q2AudioDataTreeWidget
from components.Q2AudioPlayerWidget import Q2AudioPlayerWidget
from components.Q2MetadataManager import Q2MetadataManager


class Q2MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)

        self.metadata_manager = Q2MetadataManager(None)
        self.audio_player = Q2AudioPlayerWidget(None, self.metadata_manager)
        self.audio_data_tree = Q2AudioDataTreeWidget(None, self.metadata_manager)

        self.audio_data_tree.played.connect(self.audio_player.played_from_audio_tree)

        self.app_main_widget = QWidget()
        self.setCentralWidget(self.app_main_widget)
        self.app_main_widget.setLayout(QHBoxLayout())

        self.app_info_widget = QWidget()

        self.app_main_widget.layout().addWidget(self.audio_player)
        self.app_main_widget.layout().addWidget(self.app_info_widget)

        self.app_info_widget.setLayout(QVBoxLayout())
        self.app_info_widget.layout().addWidget(self.metadata_manager)
        self.app_info_widget.layout().addWidget(self.audio_data_tree)
