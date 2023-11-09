from typing import Union

import PySide6
import pyaudio
import pydub
from PySide6.QtCore import QObject, Signal, Slot, QThread, QTime
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from pydub import AudioSegment

from components.Q2MetadataManager import Q2MetadataManager


class Q2AudioPlayerWidget(QWidget):
    __thread_played: Signal = Signal(str, str)

    def __init__(self, parent: PySide6.QtWidgets.QWidget, metadata_manager: Q2MetadataManager):
        super().__init__(parent=parent)

        # data
        self.__metadata_manager = metadata_manager
        self.__audio_player_thread = QThread()

        # widgets
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.pause_button = QPushButton(text="Pause")
        self.resume_button = QPushButton(text="Resume")
        self.layout.addWidget(self.resume_button)
        self.layout.addWidget(self.pause_button)

        self.__audio_worker = AudioWorker(metadata_manager)
        self.__audio_worker.moveToThread(self.__audio_player_thread)
        self.__audio_player_thread.started.connect(self.__audio_worker.start)
        self.__audio_player_thread.start()
        self.__thread_played.connect(self.__audio_worker.play)
        self.pause_button.released.connect(self.__thread_pause)
        self.resume_button.released.connect(self.__thread_resume)

    @Slot(str, str)
    def played_from_audio_tree(self, file_path, track_name):
        self.__audio_worker.play(file_path, track_name)

    def __thread_resume(self):
        self.__audio_worker.resume()

    def __thread_pause(self):
        self.__audio_worker.pause()


class AudioWorker(QObject):

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
                if self.current_frame >= self.loop_end_frame:
                    self.current_frame = self.loop_start_frame

    @Slot()
    def resume(self):
        # if self.__audio_stream is None or self.__audio_stream.is_active():
        if self.__audio_stream is None:
            return
        self.is_playing = True

    @Slot()
    def pause(self):
        self.is_playing = False

    @Slot()
    def stop(self):
        self.__do_loop = False

    @Slot(str, str)
    def play(self, file_path: str, track_name: str):
        self.is_playing = False
        self.__audio_stream.close() if self.__audio_stream is not None else ""
        self.current_song_path = file_path
        self.current_song_track = track_name
        self.current_frame = 0
        self.__audio_segment = AudioSegment.from_file(file_path)
        self.__frame_rate = self.__audio_segment.frame_rate
        print(self.__frame_rate)
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
        self.is_playing = True
