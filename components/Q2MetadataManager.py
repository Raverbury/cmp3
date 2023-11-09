import PySide6
from PySide6.QtCore import QFileSystemWatcher, Slot, QFile, Signal, QByteArray
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout
import json


class Q2MetadataManager(QWidget):
    metadata_changed = Signal(dict)

    def __init__(self, parent: PySide6.QtWidgets.QWidget):
        super().__init__(parent=parent)

        # internal data
        self.__FILE_PATH = "metadata.json"
        self.metadata_object: dict = dict()
        self.__q_file = QFile(self.__FILE_PATH)

        # widgets/layouts
        self.__layout = QHBoxLayout()
        self.setLayout(self.__layout)
        self.__refresh_button = QPushButton(parent=self, text="Refresh")
        self.__refresh_button.pressed.connect(self.refresh_metadata)
        self.__open_file_button = QPushButton(parent=self, text="Open metadata.json")
        self.__open_file_button.pressed.connect(self.open_metadata)
        self.__layout.addWidget(self.__refresh_button)
        self.__layout.addWidget(self.__open_file_button)

        # setup
        self.refresh_metadata()

    @Slot()
    def refresh_metadata(self):
        self.create_file_if_not_exist()
        self.__q_file.open(PySide6.QtCore.QIODevice.OpenModeFlag.ReadOnly)
        json_string = self.__q_file.readAll().toStdString()
        self.__q_file.close()
        if json_string == "":
            json_object = dict()
        else:
            json_object = json.loads(json_string)

        print(json_object)
        self.metadata_object = json_object
        self.metadata_changed.emit(self.metadata_object)

    def save_to_file(self):
        self.create_file_if_not_exist()
        self.__q_file.open(PySide6.QtCore.QIODevice.OpenModeFlag.WriteOnly)
        self.__q_file.write(QByteArray().fromStdString(json.dumps(self.metadata_object)))
        self.__q_file.close()

    @Slot()
    def open_metadata(self):
        self.create_file_if_not_exist()
        q_desktop_services = QDesktopServices()
        q_desktop_services.openUrl(self.__FILE_PATH)

    def create_file_if_not_exist(self):
        if not self.__q_file.exists():
            self.__q_file.open(PySide6.QtCore.QIODevice.OpenModeFlag.NewOnly)
            self.__q_file.close()

    def get_loop_times(self, file_path: str, track_name: str):
        return self.metadata_object[file_path][track_name]

    def remove_track(self, file_path: str, track_name: str):
        self.metadata_object[file_path].pop(track_name)
        self.save_to_file()
        self.metadata_changed.emit(self.metadata_object)
