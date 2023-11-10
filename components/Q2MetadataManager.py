import json
from collections import OrderedDict

import PySide6
from PySide6.QtCore import QFileSystemWatcher, Slot, QFile, Signal, QByteArray, QTime
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox
from pydub import AudioSegment


class Q2MetadataManager(QWidget):
    metadata_changed = Signal(OrderedDict)
    add_new_song_requested = Signal()
    new_edit_requested = Signal(str, str)

    def __init__(self, parent: PySide6.QtWidgets.QWidget):
        super().__init__(parent=parent)

        # internal data
        self.__FILE_PATH = "metadata.json"
        self.metadata_object: OrderedDict = OrderedDict()
        self.__q_file = QFile(self.__FILE_PATH)

        # widgets/layouts
        self.__layout1 = QVBoxLayout()
        self.__layout2 = QHBoxLayout()
        self.setLayout(self.__layout1)
        self.__layout1.addLayout(self.__layout2)
        self.__reload_button = QPushButton(parent=self, text="Reload")
        self.__reload_button.clicked.connect(self.reload_metadata)
        self.__open_file_button = QPushButton(parent=self, text="Open metadata.json")
        self.__open_file_button.clicked.connect(self.open_metadata)
        self.__layout2.addWidget(self.__reload_button)
        self.__layout2.addWidget(self.__open_file_button)
        self.__add_song_button = QPushButton(parent=self, text="Add a new song")
        self.__layout1.addWidget(self.__add_song_button)
        self.__add_song_button.clicked.connect(self.__add_new_song_button_clicked)

        # setup
        self.reload_metadata()

    @Slot()
    def reload_metadata(self):
        self.create_file_if_not_exist()
        self.__q_file.open(PySide6.QtCore.QIODevice.OpenModeFlag.ReadOnly)
        json_string = self.__q_file.readAll().toStdString()
        self.__q_file.close()
        if json_string == "":
            json_object = OrderedDict()
        else:
            try:
                json_object = OrderedDict(json.loads(json_string))
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
                return

        if not self.validate(json_object):
            return
        self.metadata_object = json_object
        self.metadata_changed.emit(json_object)

    def validate(self, json_object):
        try:
            for song in json_object.keys():
                for track in json_object[song].keys():
                    times = json_object[song][track]
                    q_time = QTime.fromString(times[0], "hh:mm:ss.zzz")
                    q_time2 = QTime.fromString(times[1], "hh:mm:ss.zzz")
                    if not q_time.isValid():
                        raise InvalidTimeFormat(times[0])
                    if not q_time2.isValid():
                        raise InvalidTimeFormat(times[1])
                    if q_time > q_time2:
                        raise InvalidTimeFormat(
                            f"Loop start time cannot be greater than loop end time in {song}:{track}")
        except KeyError as e:
            QMessageBox.critical(self, "Error", f"Malformed json ({str(e)})")
            return False
        except TypeError as e:
            QMessageBox.critical(self, "Error", f"Malformed json ({str(e)})")
            return False
        except InvalidTimeFormat as e:
            QMessageBox.critical(self, "Error", f"Invalid time format ({str(e)})")
            return False
        return True

    def save_to_file(self):
        self.create_file_if_not_exist()
        self.__q_file.open(PySide6.QtCore.QIODevice.OpenModeFlag.WriteOnly)
        self.__q_file.write(QByteArray().fromStdString(json.dumps(self.metadata_object, indent=4)))
        self.__q_file.close()

    @Slot()
    def open_metadata(self):
        self.create_file_if_not_exist()
        q_desktop_services = QDesktopServices()
        q_desktop_services.openUrl(self.__FILE_PATH)

    @Slot()
    def __add_new_song_button_clicked(self):
        self.add_new_song_requested.emit()

    @Slot(str)
    def new_file_added(self, file_path):
        if file_path in self.metadata_object.keys():
            QMessageBox.critical(self, "Error", "Duplicate file")
            return
        if not QFile(file_path).exists():
            QMessageBox.critical(self, "Error", f"Cannot find {file_path}")
            return
        self.metadata_object[file_path] = dict()
        track_name = self.add_track(file_path)
        self.new_edit_requested.emit(file_path, track_name)

    def create_file_if_not_exist(self):
        if not self.__q_file.exists():
            self.__q_file.open(PySide6.QtCore.QIODevice.OpenModeFlag.NewOnly)
            self.__q_file.close()

    def get_loop_times(self, file_path: str, track_name: str):
        return self.metadata_object[file_path][track_name]

    def remove_song(self, file_path):
        self.metadata_object.pop(file_path)
        self.save_to_file()
        self.metadata_changed.emit(self.metadata_object)

    def remove_track(self, file_path: str, track_name: str):
        self.metadata_object[file_path].pop(track_name)
        self.save_to_file()
        self.metadata_changed.emit(self.metadata_object)

    def update_track(self, file_path: str, old_track_name: str, new_track_name: str, loop_from: str, loop_to: str):
        if old_track_name == new_track_name:
            self.metadata_object[file_path][old_track_name] = [loop_from, loop_to]
        else:
            self.metadata_object[file_path].pop(old_track_name)
            self.metadata_object[file_path][new_track_name] = [loop_from, loop_to]
        self.save_to_file()
        self.metadata_changed.emit(self.metadata_object)

    @Slot(str)
    def add_track(self, file_path):
        track_name = "New track"
        i = 1
        try_track_name = track_name
        while try_track_name in self.metadata_object[file_path].keys():
            try_track_name = f"{track_name} ({i})"
            i = i + 1
        audio_segment = AudioSegment.from_file(file_path)
        duration_ms = int(audio_segment.duration_seconds * 1000)
        q_time = QTime().fromMSecsSinceStartOfDay(duration_ms)
        self.metadata_object[file_path][try_track_name] = ["00:00:00.000", q_time.toString("hh:mm:ss.zzz")]
        self.save_to_file()
        self.metadata_changed.emit(self.metadata_object)
        return try_track_name


class InvalidTimeFormat(Exception):
    def __int__(self, reason):
        self.args = reason
