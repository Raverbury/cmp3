import PySide6
from PySide6.QtCore import Qt, Slot, QTime, Signal
from PySide6.QtWidgets import QDialog, QFormLayout, QPushButton, QVBoxLayout, QDialogButtonBox, QLineEdit, QTimeEdit, \
    QMessageBox
from pydub import AudioSegment

from components.Q2MetadataManager import Q2MetadataManager


class Q2TrackEditDialog(QDialog):
    edit_submitted = Signal(str, str, str, str, str)

    def __init__(self, parent: PySide6.QtWidgets.QWidget, metadata_manager: Q2MetadataManager):
        super().__init__(parent)

        self.setWindowTitle("Edit track")
        self.__metadata_manager = metadata_manager

        self.setModal(True)
        self.resize(600, 200)

        self.__layout1 = QVBoxLayout()
        self.__layout2 = QFormLayout()
        self.__layout2.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.__layout2.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.__button_box = QDialogButtonBox()
        self.setLayout(self.__layout1)
        self.__layout1.addLayout(self.__layout2)
        self.__layout1.addWidget(self.__button_box)

        self.song_line_edit = QLineEdit()
        self.song_line_edit.setEnabled(False)
        self.__layout2.addRow("File path:", self.song_line_edit)

        self.old_track_line_edit = QLineEdit()
        self.old_track_line_edit.setEnabled(False)
        self.__layout2.addRow("Old track name:", self.old_track_line_edit)

        self.new_track_line_edit = QLineEdit()
        self.__layout2.addRow("New track name:", self.new_track_line_edit)

        self.loop_from_time_edit = QTimeEdit()
        self.loop_from_time_edit.setDisplayFormat("hh:mm:ss.zzz")
        # self.loop_from_time_edit.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.__layout2.addRow("Loop from:", self.loop_from_time_edit)

        self.loop_to_time_edit = QTimeEdit()
        self.loop_to_time_edit.setDisplayFormat("hh:mm:ss.zzz")
        # self.loop_to_time_edit.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.__layout2.addRow("Loop to:", self.loop_to_time_edit)

        self.save_button = QPushButton(parent=self, text="Save")
        self.cancel_button = QPushButton(parent=self, text="Cancel")

        self.save_button.clicked.connect(self.apply)
        self.cancel_button.clicked.connect(self.cancel)

        self.__button_box.addButton(self.save_button, QDialogButtonBox.ButtonRole.AcceptRole)
        self.__button_box.addButton(self.cancel_button, QDialogButtonBox.ButtonRole.NoRole)

    @Slot(str, str)
    def open_new(self, file_path, track_name):
        self.song_line_edit.setText(file_path)
        self.old_track_line_edit.setText(track_name)
        self.new_track_line_edit.setText(track_name)
        self.new_track_line_edit.setFocus()
        times = self.__metadata_manager.metadata_object[file_path][track_name]
        max_duration = int(AudioSegment.from_file(file_path).duration_seconds * 1000)
        self.loop_from_time_edit.setTime(QTime.fromString(times[0], "hh:mm:ss.zzz"))
        self.loop_from_time_edit.setMaximumTime(QTime.fromMSecsSinceStartOfDay(max_duration))
        self.loop_to_time_edit.setTime(QTime.fromString(times[1], "hh:mm:ss.zzz"))
        self.loop_to_time_edit.setMaximumTime(QTime.fromMSecsSinceStartOfDay(max_duration))
        self.cancel_button.clearFocus()
        self.save_button.clearFocus()
        self.open()

    @Slot()
    def cancel(self):
        self.close()

    @Slot()
    def apply(self):
        file_path = self.song_line_edit.text()
        old_track_name = self.old_track_line_edit.text()
        new_track_name = self.new_track_line_edit.text()
        from_time_string = self.loop_from_time_edit.time().toString("hh:mm:ss.zzz")
        to_time_string = self.loop_to_time_edit.time().toString("hh:mm:ss.zzz")
        if (new_track_name != old_track_name and
                new_track_name in self.__metadata_manager.metadata_object[file_path].keys()):
            QMessageBox.critical(self, "Error", "Duplicate track name")
            return
        if (self.loop_from_time_edit.time().msecsSinceStartOfDay() >= self
                .loop_to_time_edit.time().msecsSinceStartOfDay()):
            QMessageBox.critical(self, "Error", "Loop start time cannot be greater than loop end time")
            return
        self.edit_submitted.emit(file_path, old_track_name, new_track_name, from_time_string, to_time_string)
        self.close()
