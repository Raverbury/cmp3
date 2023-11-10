import PySide6
import pyaudio
import pydub
from PySide6.QtCore import QObject, Signal, Slot, QThread, QTime, QFile, QUrl, Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QMessageBox, QLabel, QGridLayout
from pydub import AudioSegment

from components.Q2CustomProgressBar import Q2CustomProgressBar
from components.Q2MetadataManager import Q2MetadataManager


class Q2AudioPlayerWidget(QWidget):
    __thread_played: Signal = Signal(str, str)

    def __init__(self, parent: PySide6.QtWidgets.QWidget, metadata_manager: Q2MetadataManager):
        super().__init__(parent=parent)

        # data
        self.__metadata_manager = metadata_manager
        self.__audio_player_thread = QThread()

        # widgets
        self.__layout1 = QGridLayout()
        self.__layout2 = QHBoxLayout()
        self.__song_label = QLabel()
        self.__song_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__track_label = QLabel()
        self.__track_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__progress_bar = Q2CustomProgressBar(None)
        self.setLayout(self.__layout1)
        for i in range(12):
            self.__layout1.setRowMinimumHeight(i, 20)
            self.__layout1.setRowStretch(i, 20)
        self.__layout1.addWidget(self.__song_label, 2, 0)
        self.__layout1.addWidget(self.__track_label, 3, 0)
        self.__layout1.addWidget(self.__progress_bar, 4, 0, 2, 0)
        self.__layout1.addLayout(self.__layout2, 6, 0, 2, 0)
        self.pause_button = QPushButton(text="Pause")
        self.resume_button = QPushButton(text="Resume")
        self.__layout2.addWidget(self.resume_button)
        self.__layout2.addWidget(self.pause_button)

        # ctor logic
        self.__audio_worker = AudioWorker(metadata_manager)
        self.__audio_worker.moveToThread(self.__audio_player_thread)
        self.__audio_player_thread.started.connect(self.__audio_worker.start)
        self.__audio_player_thread.start()
        self.__thread_played.connect(self.__audio_worker.play_track)
        self.pause_button.clicked.connect(self.__thread_pause)
        self.resume_button.clicked.connect(self.__thread_resume)
        self.__audio_worker.is_playing_changed.connect(self.__worker_is_playing_changed)
        self.__audio_worker.progress_updated.connect(self.__worker_progress_updated)
        self.__audio_worker.song_track_changed.connect(self.__worker_changed_song_track)

    @Slot(str, str)
    def play_track_from_tree(self, file_path, track_name):
        self.__audio_worker.play_track(file_path, track_name)

    @Slot(str)
    def play_song_from_tree(self, file_path):
        self.__audio_worker.play_song(file_path)

    @Slot()
    def __thread_resume(self):
        self.__audio_worker.resume()

    @Slot()
    def __thread_pause(self):
        self.__audio_worker.pause()

    def stop_thread(self):
        self.__audio_worker.stop()
        self.__audio_player_thread.exit(0)

    @Slot(bool)
    def __worker_is_playing_changed(self, is_playing):
        self.pause_button.setEnabled(is_playing)
        self.resume_button.setEnabled(not is_playing)

    @Slot(int, int, int, int)
    def __worker_progress_updated(self, current_frame, max_frame, loop_start_frame, loop_end_frame):
        # self.__progress_bar.setRange(0, max_frame)
        # self.__progress_bar.setValue(current_frame)
        self.__progress_bar.set_stats(current_frame, max_frame, loop_start_frame, loop_end_frame)

    @Slot(str, str)
    def __worker_changed_song_track(self, file_path, track_name):
        q_url = QUrl(file_path)
        self.__song_label.setText(q_url.fileName())
        self.__song_label.setToolTip(file_path)
        self.__track_label.setText(track_name)


class AudioWorker(QObject):
    is_playing_changed = Signal(bool)
    progress_updated = Signal(int, int, int, int)
    song_track_changed = Signal(str, str)

    def __init__(self, metadata_manager: Q2MetadataManager):
        super().__init__()
        self.__metadata_manager: Q2MetadataManager = metadata_manager

        # song/track data
        self.is_playing: bool = False
        self.current_song_path: str = ""
        self.current_song_track: str = ""
        self.current_frame: int = 0
        self.loop_start_frame: int = -1
        self.loop_end_frame: int = -1

        # audio player/frame
        self.__do_loop = True
        self.__audio_segment: pydub.audio_segment.AudioSegment = None
        self.__frame_rate: int = 0
        self.__py_audio = pyaudio.PyAudio()
        self.__audio_stream: pyaudio.Stream = None

    def set_is_playing(self, value):
        self.is_playing = value
        self.is_playing_changed.emit(value)

    @Slot()
    def start(self):
        while self.__do_loop:
            # chunk = int(float(1024.0 / self.__frame_rate) * 1000)
            chunk = 10
            while self.is_playing:
                # print(self.current_frame)
                data = (self.__audio_segment[self.current_frame:self.current_frame + chunk]).raw_data
                if data == "":
                    pass
                self.__audio_stream.write(data)
                self.current_frame += chunk
                self.progress_updated.emit(self.current_frame, int(self.__audio_segment.duration_seconds * 1000),
                                           self.loop_start_frame, self.loop_end_frame)
                if self.current_frame >= self.loop_end_frame:
                    self.current_frame = self.loop_start_frame
        self.deleteLater()

    def resume(self):
        # if self.__audio_stream is None or self.__audio_stream.is_active():
        if self.__audio_stream is None:
            return
        self.set_is_playing(True)

    def pause(self):
        self.set_is_playing(False)

    @Slot()
    def stop(self):
        self.is_playing = False
        self.__do_loop = False

    @Slot(str, str)
    def play_track(self, file_path: str, track_name: str):
        q_file = QFile(file_path)
        if not q_file.exists():
            QMessageBox.critical(self.__metadata_manager, "Error", f"Cannot find {file_path}")
            return
        self.is_playing = False
        self.__audio_stream.close() if self.__audio_stream is not None else ""
        self.current_song_path = file_path
        self.current_song_track = track_name
        self.current_frame = 0
        self.__audio_segment = AudioSegment.from_file(file_path)
        self.__frame_rate = self.__audio_segment.frame_rate
        self.__audio_stream = self.__py_audio.open(
            format=self.__py_audio.get_format_from_width(self.__audio_segment.sample_width),
            channels=self.__audio_segment.channels,
            rate=self.__frame_rate,
            output=True)
        times = self.__metadata_manager.get_loop_times(self.current_song_path, self.current_song_track)
        q_time = QTime.fromString(times[0], "hh:mm:ss.zzz")
        self.loop_start_frame = q_time.msecsSinceStartOfDay()
        q_time = QTime.fromString(times[1], "hh:mm:ss.zzz")
        self.loop_end_frame = q_time.msecsSinceStartOfDay()
        if self.loop_end_frame > int(self.__audio_segment.duration_seconds * 1000) or self.loop_start_frame > int(
                self.__audio_segment.duration_seconds * 1000):
            QMessageBox.critical(self.__metadata_manager, "Error", f"Loop times cannot exceed audio duration")
        self.song_track_changed.emit(file_path, track_name)
        self.set_is_playing(True)

    @Slot(str)
    def play_song(self, file_path):
        q_file = QFile(file_path)
        if not q_file.exists():
            QMessageBox.critical(self.__metadata_manager, "Error", f"Cannot find {file_path}")
            return
        self.is_playing = False
        self.__audio_stream.close() if self.__audio_stream is not None else ""
        self.current_song_path = file_path
        self.current_song_track = "Default"
        self.current_frame = 0
        self.__audio_segment = AudioSegment.from_file(file_path)
        self.__frame_rate = self.__audio_segment.frame_rate
        self.__audio_stream = self.__py_audio.open(
            format=self.__py_audio.get_format_from_width(self.__audio_segment.sample_width),
            channels=self.__audio_segment.channels,
            rate=self.__frame_rate,
            output=True)
        self.loop_start_frame = 0
        self.loop_end_frame = int(self.__audio_segment.duration_seconds * 1000)
        if self.loop_end_frame > int(self.__audio_segment.duration_seconds * 1000) or self.loop_start_frame > int(
                self.__audio_segment.duration_seconds * 1000):
            QMessageBox.critical(self.__metadata_manager, "Error", f"Loop times cannot exceed audio duration")
        self.song_track_changed.emit(file_path, "Default")
        self.set_is_playing(True)
