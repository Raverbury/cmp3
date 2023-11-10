import PySide6
from PySide6.QtGui import QPaintEvent, QPainter, QColor
from PySide6.QtWidgets import QProgressBar


class Q2CustomProgressBar(QProgressBar):
    def __init__(self, parent: PySide6.QtWidgets.QWidget):
        super().__init__(parent)
        self.setTextVisible(False)
        self.loop_start_frame = 0
        self.loop_end_frame = 0

    def set_stats(self, current_frame, max_frame, loop_start_frame, loop_end_frame):
        self.setValue(current_frame)
        self.setMaximum(max_frame)
        self.loop_start_frame = loop_start_frame
        self.loop_end_frame = loop_end_frame
        self.update()

    def paintEvent(self, event: QPaintEvent):
        super().paintEvent(event)
        q_painter = QPainter(self)
        q_painter.fillRect(int(self.width() * self.loop_start_frame / self.maximum()), 1,
                           1, self.height() - 1,
                           QColor(130, 0, 0, 255))
        q_painter.fillRect(int(self.width() * self.loop_end_frame / self.maximum()) - 1, 1,
                           1, self.height() - 1,
                           QColor(130, 0, 0, 255))
        q_painter.end()
