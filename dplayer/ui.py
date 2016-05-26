from core import DPlayerCore
import sys
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (QApplication, QPushButton, QWidget, QSlider,
                             QTableView, QGridLayout, QDesktopWidget,
                             QFileDialog)
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtGui import QIcon, QKeySequence


class DPlayerUI(QWidget):
    def __init__(self):
        super().__init__()

        self.playerCore = DPlayerCore()
        self.initUI()

    def initUI(self):
        self.grid = QGridLayout()
        self.grid.setRowMinimumHeight(0, 100)

        self.initButtons()
        self.initVolumeSlider()
        self.initTimeSlider()
        # self.initSongLabel()

        self.playlist = QTableView()
        self.playlist.setFocusPolicy(Qt.NoFocus)
        self.grid.addWidget(self.playlist, 2, 0, 1, 5)

        self.setLayout(self.grid)
        self.setWindowTitle('DPlayer')
        self.setWindowIcon(QIcon('icons/logo.png'))
        self.center()
        self.show()

    def initButtons(self):
        self.buttons = {}
        self.buttonNames = ['stop', 'previous', 'play', 'next', 'mute', 'add']
        shortcuts = ['z', 'x', 'c', 'v', 'b', 'a']

        for name, cut, position in zip(self.buttonNames, shortcuts, range(6)):
            button = QPushButton(self)
            button.setIcon(QIcon('icons/{}.png'.format(name)))
            button.setIconSize(QSize(20, 20))
            button.resize(button.sizeHint())
            button.setFocusPolicy(Qt.NoFocus)
            button.setToolTip(name)
            button.setShortcut(QKeySequence(cut))
            self.buttons[name] = button
            self.grid.addWidget(button, 1, position)

        self.buttons['stop'].clicked.connect(self.stopClicked)
        self.buttons['previous'].clicked.connect(self.playerCore.previous)
        self.buttons['play'].clicked.connect(self.playClicked)
        self.buttons['next'].clicked.connect(self.playerCore.next)
        self.buttons['mute'].clicked.connect(self.muteClicked)
        self.buttons['mute'].setIcon(QIcon('icons/volume_middle.png'))
        self.buttons['add'].clicked.connect(self.addClicked)
        self.grid.removeWidget(self.buttons['add'])
        self.grid.addWidget(self.buttons['add'], 3, 0)

    def stopClicked(self):
        self.playerCore.stop()
        self.buttons['play'].setIcon(QIcon('icons/play.png'))
        self.buttons['play'].setToolTip('play')

    def playClicked(self):
        if self.playerCore.state() in (QMediaPlayer.StoppedState,
                                       QMediaPlayer.PausedState):
            self.playerCore.play()
            self.buttons['play'].setIcon(QIcon('icons/pause.png'))
            self.buttons['play'].setToolTip('pause')
        else:   # QMediaPlayer.PlayingState
            self.playerCore.pause()
            self.buttons['play'].setIcon(QIcon('icons/play.png'))
            self.buttons['play'].setToolTip('play')

    def muteClicked(self):
        if self.playerCore.isMuted():
            self.playerCore.unmute()
            self.changeValue(self.currentVolume)
        else:
            self.playerCore.mute()
            self.changeValue(0)

    def addClicked(self):
        fileNames, _ = QFileDialog.getOpenFileNames(self, 'Add music')
        self.playerCore.add(fileNames)

    def initVolumeSlider(self):
        self.volumeSlider = QSlider(Qt.Vertical, self)
        self.volumeSlider.setRange(0, 100)
        self.currentVolume = 70
        self.volumeSlider.setValue(self.currentVolume)
        self.volumeSlider.setFocusPolicy(Qt.NoFocus)
        self.volumeSlider.setToolTip('volume: {}'.format(
            str(self.volumeSlider.value())))
        self.volumeSlider.valueChanged[int].connect(self.changeValue)
        self.grid.addWidget(self.volumeSlider, 0, 4, Qt.AlignHCenter)

    def changeValue(self, value):
        self.playerCore.volume(value)

        if value == 0:
            self.buttons['mute'].setIcon(QIcon('icons/mute.png'))
        elif 0 < value <= 35:
            self.buttons['mute'].setIcon(QIcon('icons/volume_min.png'))
            self.playerCore.unmute
        elif 35 < value <= 70:
            self.buttons['mute'].setIcon(QIcon('icons/volume_middle.png'))
            self.playerCore.unmute
        else:   # 70 < value <= 100
            self.buttons['mute'].setIcon(QIcon('icons/volume_max.png'))
            self.playerCore.unmute

        self.volumeSlider.setValue(value)
        self.volumeSlider.setToolTip('volume: {}'.format(str(value)))

        if self.playerCore.isMuted():
            self.buttons['mute'].setToolTip('unmute')
        else:
            self.currentVolume = value
            self.buttons['mute'].setToolTip('mute')

    def initTimeSlider(self):
        self.timeSlider = QSlider(Qt.Horizontal, self)
        # self.timeSlider.setRange(0, 100)  # song length
        self.currentTime = 0
        self.timeSlider.setValue(self.currentTime)
        self.timeSlider.setFocusPolicy(Qt.NoFocus)
        self.timeSlider.setToolTip('time: {}'.format(
            str(self.timeSlider.value())))
        self.timeSlider.valueChanged[int].connect(self.changeTime)
        self.grid.addWidget(self.timeSlider, 0, 0, 1, 4, Qt.AlignBottom)

    def changeTime(self, value):
        pass

    # def initSongLabel(self):
    #     self.songLabel = QLabel()   # song title
    #     self.grid.addWidget(self.songLabel, 0, 0, 1, 4, Qt.AlignVCenter)

    def center(self):
        # rectangle specifying the geometry of the widget
        rectangle = self.frameGeometry()
        # screen resolution -> center point
        centerPoint = QDesktopWidget().availableGeometry().center()
        # set the center of the rectangle to the center of the screen
        rectangle.moveCenter(centerPoint)
        # move the top-left point of the application window to the top-left
        # point of the rectangle
        self.move(rectangle.topLeft())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = DPlayerUI()
    sys.exit(app.exec_())
