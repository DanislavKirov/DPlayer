from core import DPlayerCore
import sys
from PyQt5.QtCore import Qt, QSize, QTime
from PyQt5.QtWidgets import (QApplication, QPushButton, QWidget, QSlider,
                             QTableWidget, QGridLayout, QDesktopWidget,
                             QFileDialog, QTableWidgetItem, QAbstractItemView,
                             QLabel)
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtGui import QIcon, QKeySequence


class DPlayerUI(QWidget):
    def __init__(self):
        super().__init__()

        self.playerCore = DPlayerCore()
        self.player = self.playerCore.player
        self.playlist = self.playerCore.playlist
        self.initUI()

    def initUI(self):
        self.grid = QGridLayout()
        self.grid.setRowMinimumHeight(0, 100)

        self.initButtons()
        self.initVolumeSlider()
        self.initDurationSlider()
        self.initDurationLabel()
        # self.initSongLabel()
        self.initPlaylist()

        self.player.durationChanged.connect(self.durationChanged)
        self.player.positionChanged.connect(self.positionChanged)
        self.player.stateChanged.connect(self.checkStpped)

        self.setLayout(self.grid)
        self.setGeometry(0, 0, 450, 400)
        self.setWindowTitle('DPlayer')
        self.setWindowIcon(QIcon('icons/logo.png'))
        self.center()
        self.show()

    def initButtons(self):
        self.buttons = {}
        self.buttonNames = ['stop', 'previous', 'play', 'next', 'mute', 'add',
                            'shuffle', 'repeatPlaylist', 'repeatSong']
        shortcuts = ['z', 'x', 'c', 'v', 'b', 'a', 's', 'd', 'f']

        for name, cut, position in zip(self.buttonNames, shortcuts, range(9)):
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
        self.buttons['next'].clicked.connect(self.nextClicked)
        self.buttons['mute'].clicked.connect(self.muteClicked)
        self.buttons['mute'].setIcon(QIcon('icons/volumeMiddle.png'))

        for name, position in zip(self.buttonNames[5:], range(4)):
            self.grid.removeWidget(self.buttons[name])
            self.grid.addWidget(self.buttons[name], 3, position)

        self.buttons['add'].clicked.connect(self.addClicked)
        self.buttons['shuffle'].setCheckable(True)
        self.buttons['shuffle'].clicked[bool].connect(
            self.shuffleClicked)
        self.buttons['repeatPlaylist'].setCheckable(True)
        self.buttons['repeatPlaylist'].clicked[bool].connect(
            self.repeatPlaylistClicked)
        self.buttons['repeatSong'].setCheckable(True)
        self.buttons['repeatSong'].clicked[bool].connect(
            self.repeatSongClicked)

    def stopClicked(self):
        self.playerCore.stop()
        self.buttons['play'].setIcon(QIcon('icons/play.png'))
        self.buttons['play'].setToolTip('play')
        self.durationLabel.setText('00:00 / 00:00')

    def playClicked(self):
        if self.playerCore.state() in (QMediaPlayer.StoppedState,
                                       QMediaPlayer.PausedState):
            self.playerCore.play()
            if self.playerCore.state() == QMediaPlayer.PlayingState:
                self.buttons['play'].setIcon(QIcon('icons/pause.png'))
                self.buttons['play'].setToolTip('pause')
        else:   # QMediaPlayer.PlayingState
            self.playerCore.pause()
            self.buttons['play'].setIcon(QIcon('icons/play.png'))
            self.buttons['play'].setToolTip('play')

    def nextClicked(self):
        if not self.playerCore.repeatingSong and \
           not self.playerCore.shuffling and \
           not self.playerCore.repeatingPlaylist and \
           self.playlist.currentIndex() + 1 == self.playerCore.numberOfSongs():
            self.stopClicked()
        else:
            self.playerCore.next()

    def muteClicked(self):
        if self.playerCore.isMuted():
            self.playerCore.unmute()
            self.volumeChanged(self.currentVolume)
        else:
            self.playerCore.mute()
            self.volumeChanged(0)

    def addClicked(self):
        fileNames, _ = QFileDialog.getOpenFileNames(self, 'Add music')
        self.playerCore.add(fileNames)

        songsToAdd = len(fileNames)
        for name, row in zip(fileNames, range(songsToAdd)):
            currentRow = row + self.playerCore.numberOfSongs() - songsToAdd
            self.playlistTable.insertRow(currentRow)
            artist = self.playerCore.getArtist(name)[0]
            self.playlistTable.setItem(currentRow, 0, QTableWidgetItem(artist))
            title = self.playerCore.getTitle(name)[0]
            self.playlistTable.setItem(currentRow, 1, QTableWidgetItem(title))
            album = self.playerCore.getAlbum(name)[0]
            self.playlistTable.setItem(currentRow, 2, QTableWidgetItem(album))
            minutes = int(round(self.playerCore.getDuration(name) / 60, 0))
            seconds = int(round(self.playerCore.getDuration(name) % 60, 0))
            duration = '{}:{}'.format(minutes, seconds)
            self.playlistTable.setItem(
                currentRow, 3, QTableWidgetItem(duration))

        self.playlistTable.resizeColumnToContents(0)
        self.playlistTable.resizeColumnToContents(1)
        self.playlistTable.resizeColumnToContents(2)
        self.playlistTable.resizeColumnToContents(3)

    def shuffleClicked(self, pressed):
        self.playerCore.shuffle(pressed)

    def repeatPlaylistClicked(self, pressed):
        self.playerCore.repeatPlaylist(pressed)

    def repeatSongClicked(self, pressed):
        self.playerCore.repeatSong(pressed)

    def initVolumeSlider(self):
        self.volumeSlider = QSlider(Qt.Vertical, self)
        self.volumeSlider.setRange(0, 100)
        self.currentVolume = 70
        self.volumeSlider.setValue(self.currentVolume)
        self.volumeSlider.setFocusPolicy(Qt.NoFocus)
        self.volumeSlider.setToolTip('volume: {}'.format(
            str(self.volumeSlider.value())))
        self.volumeSlider.valueChanged[int].connect(self.volumeChanged)
        self.grid.addWidget(self.volumeSlider, 0, 4, Qt.AlignHCenter)

    def volumeChanged(self, value):
        self.playerCore.volume(value)

        if value == 0:
            self.buttons['mute'].setIcon(QIcon('icons/mute.png'))
        elif 0 < value <= 35:
            self.buttons['mute'].setIcon(QIcon('icons/volumeMin.png'))
            self.playerCore.unmute
        elif 35 < value <= 70:
            self.buttons['mute'].setIcon(QIcon('icons/volumeMiddle.png'))
            self.playerCore.unmute
        else:   # 70 < value <= 100
            self.buttons['mute'].setIcon(QIcon('icons/volumeMax.png'))
            self.playerCore.unmute

        self.volumeSlider.setValue(value)
        self.volumeSlider.setToolTip('volume: {}'.format(str(value)))

        if self.playerCore.isMuted():
            self.buttons['mute'].setToolTip('unmute')
        else:
            self.currentVolume = value
            self.buttons['mute'].setToolTip('mute')

    def initDurationSlider(self):
        self.durationSlider = QSlider(Qt.Horizontal, self)
        self.durationSlider.setValue(0)
        self.durationSlider.setFocusPolicy(Qt.NoFocus)
        # self.durationSlider.valueChanged[int].connect(self.positionChanged)
        self.grid.addWidget(self.durationSlider, 0, 0, 1, 3, Qt.AlignBottom)

    def initDurationLabel(self):
        self.durationLabel = QLabel('00:00 / 00:00')
        self.grid.addWidget(self.durationLabel, 0, 3, Qt.AlignBottom)

    def durationChanged(self, value):
        self.durationSlider.setMaximum(value / 1000)

    def positionChanged(self, value):
        seconds = value / 1000
        self.durationSlider.setValue(seconds)

        duration = self.player.duration() / 1000
        totalTime = QTime(0, (duration / 60) % 60, duration % 60)
        currentTime = QTime(0, (seconds / 60) % 60, seconds % 60)

        format = 'mm:ss'
        time = '{} / {}'.format(currentTime.toString(format),
                                totalTime.toString(format))
        self.durationLabel.setText(time)

    def checkStpped(self):
        if self.playerCore.state() == QMediaPlayer.StoppedState:
            self.stopClicked()

    # def initSongLabel(self):
    #     self.songLabel = QLabel()   # song title
    #     self.grid.addWidget(self.songLabel, 0, 0, 1, 4, Qt.AlignVCenter)

    def initPlaylist(self):
        self.playlistTable = QTableWidget()
        self.playlistTable.setColumnCount(4)
        self.playlistTable.setHorizontalScrollMode(
            QAbstractItemView.ScrollPerPixel)
        self.playlistTable.setHorizontalHeaderLabels(
            ['Artist', 'Title', 'Album', 'Duration'])
        self.playlistTable.setFocusPolicy(Qt.NoFocus)
        self.grid.addWidget(self.playlistTable, 2, 0, 1, 5)

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
