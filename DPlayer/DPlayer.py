import sys
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QUrl, QFileInfo
from PyQt5.QtWidgets import (QApplication, QPushButton, QGridLayout, QWidget,
                             QSlider, QDesktopWidget, QTableView, QFileDialog)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from PyQt5.QtGui import QIcon, QKeySequence


class PlayerControlsUI(QWidget):
    stopSignal = pyqtSignal()
    previousSignal = pyqtSignal()
    playSignal = pyqtSignal()
    pauseSignal = pyqtSignal()
    nextSignal = pyqtSignal()
    muteSignal = pyqtSignal(bool)
    volumeSignal = pyqtSignal(int)
    timeSignal = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.state = QMediaPlayer.StoppedState
        self.isMuted = False

        self.initButtons()
        self.initVolumeSlider()
        self.initTimeSlider()
        # self.initSongLabel()

    def initButtons(self):
        self.buttons = {}
        self.buttonNames = ['stop', 'previous', 'play', 'next', 'mute']
        shortcuts = ['z', 'x', 'c', 'v', 'b']

        for name, cut in zip(self.buttonNames, shortcuts):
            button = QPushButton(self)
            button.setIcon(QIcon('icons/{}.png'.format(name)))
            button.setIconSize(QSize(20, 20))
            button.resize(button.sizeHint())
            button.setFocusPolicy(Qt.NoFocus)
            button.setToolTip(name)
            button.setShortcut(QKeySequence(cut))
            self.buttons[name] = button

        self.buttons['stop'].clicked.connect(self.stopClicked)
        self.buttons['previous'].clicked.connect(self.previousSignal)
        self.buttons['play'].clicked.connect(self.playClicked)
        self.buttons['next'].clicked.connect(self.nextSignal)
        self.buttons['mute'].clicked.connect(self.muteClicked)
        self.buttons['mute'].setIcon(QIcon('icons/volume_middle.png'))

    def stopClicked(self):
        self.state = QMediaPlayer.StoppedState
        self.buttons['play'].setIcon(QIcon('icons/play.png'))
        self.buttons['play'].setToolTip('play')
        self.stopSignal.emit()

    def playClicked(self):
        if self.state in (QMediaPlayer.StoppedState, QMediaPlayer.PausedState):
            self.state = QMediaPlayer.PlayingState
            self.buttons['play'].setIcon(QIcon('icons/pause.png'))
            self.buttons['play'].setToolTip('pause')
            self.playSignal.emit()
        else:   # QMediaPlayer.PlayingState
            self.state = QMediaPlayer.PausedState
            self.buttons['play'].setIcon(QIcon('icons/play.png'))
            self.buttons['play'].setToolTip('play')
            self.pauseSignal.emit()

    def muteClicked(self):
        if not self.isMuted:
            self.isMuted = True
            self.changeValue(0)
        else:
            self.isMuted = False
            self.changeValue(self.currentVolume)

        self.muteSignal.emit(self.isMuted)

    def initVolumeSlider(self):
        self.volumeSlider = QSlider(Qt.Vertical, self)
        self.volumeSlider.setRange(0, 100)
        self.currentVolume = 70
        self.volumeSlider.setValue(self.currentVolume)
        self.volumeSlider.setFocusPolicy(Qt.NoFocus)
        self.volumeSlider.setToolTip('volume: {}'.format(
            str(self.volumeSlider.value())))
        self.volumeSlider.valueChanged[int].connect(self.changeValue)

    def changeValue(self, value):
        if value == 0:
            self.buttons['mute'].setIcon(QIcon('icons/mute.png'))
        elif 0 < value <= 35:
            self.isMuted = False
            self.buttons['mute'].setIcon(QIcon('icons/volume_min.png'))
        elif 35 < value <= 70:
            self.isMuted = False
            self.buttons['mute'].setIcon(QIcon('icons/volume_middle.png'))
        else:   # 70 < value <= 100
            self.isMuted = False
            self.buttons['mute'].setIcon(QIcon('icons/volume_max.png'))

        self.volumeSlider.setValue(value)
        self.volumeSlider.setToolTip('volume: {}'.format(str(value)))

        if not self.isMuted:
            self.currentVolume = value
            self.buttons['mute'].setToolTip('mute')
        else:
            self.buttons['mute'].setToolTip('unmute')

        self.volumeSignal.emit(value)

    def initTimeSlider(self):
        self.timeSlider = QSlider(Qt.Horizontal, self)
        # self.timeSlider.setRange(0, 100)  # song length
        self.currentTime = 0
        self.timeSlider.setValue(self.currentTime)
        self.timeSlider.setFocusPolicy(Qt.NoFocus)
        self.timeSlider.setToolTip('time: {}'.format(
            str(self.timeSlider.value())))
        self.timeSlider.valueChanged[int].connect(self.changeTime)

    def changeTime(self, value):
        self.timeSignal.emit(value)

    # def initSongLabel(self):
    #     self.songLabel = QLabel()   # song title
    #     self.grid.addWidget(self.songLabel, 0, 0, 1, 4, Qt.AlignVCenter)

    def addToGrid(self, grid):
        for name, position in zip(self.buttonNames, range(5)):
            grid.addWidget(self.buttons[name], 1, position)
        grid.addWidget(self.volumeSlider, 0, 4, Qt.AlignHCenter)
        grid.addWidget(self.timeSlider, 0, 0, 1, 4, Qt.AlignBottom)


class PlaylistUI(QWidget):
    addSignal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.playlist = QTableView()
        self.playlist.setFocusPolicy(False)

        self.addButton = QPushButton(self)
        self.addButton.setIcon(QIcon('icons/add.png'))
        self.addButton.setIconSize(QSize(20, 20))
        self.addButton.setFocusPolicy(False)
        self.addButton.resize(self.addButton.sizeHint())
        self.addButton.setToolTip('add')
        self.addButton.setShortcut(QKeySequence('a'))
        self.addButton.clicked.connect(self.addSignal)

    def addToGrid(self, grid):
        grid.addWidget(self.playlist, 2, 0, 1, 5)
        grid.addWidget(self.addButton, 3, 0)


class DPlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.player = QMediaPlayer()
        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)

        self.grid = QGridLayout()
        self.grid.setRowMinimumHeight(0, 100)

        self.controls = PlayerControlsUI()
        self.controls.addToGrid(self.grid)

        self.controls.stopSignal.connect(self.player.stop)
        self.controls.playSignal.connect(self.player.play)
        self.controls.pauseSignal.connect(self.player.pause)
        self.controls.muteSignal.connect(self.player.setMuted)
        self.controls.volumeSignal.connect(self.player.setVolume)

        self.controls.previousSignal.connect(self.playlist.previous)
        self.controls.nextSignal.connect(self.playlist.next)

        self.playlistUI = PlaylistUI()
        self.playlistUI.addToGrid(self.grid)

        self.playlistUI.addSignal.connect(self.add)

        self.setLayout(self.grid)
        self.setWindowTitle('DPlayer')
        self.setWindowIcon(QIcon('icons/logo.png'))
        self.center()
        self.show()

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

    def add(self):
        fileNames, _ = QFileDialog.getOpenFileNames(self, 'Add music')
        self.addToPlaylist(fileNames)

    def addToPlaylist(self, fileNames):
        for name in fileNames:
            url = QUrl.fromLocalFile(QFileInfo(name).absoluteFilePath())
            self.playlist.addMedia(QMediaContent(url))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = DPlayer()
    sys.exit(app.exec_())
