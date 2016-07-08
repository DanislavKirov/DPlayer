import os
from PyQt5.QtCore import Qt, QSize, QTime, QUrl
from PyQt5.QtWidgets import (QPushButton, QWidget, QSlider,
                             QTableWidget, QGridLayout, QDesktopWidget,
                             QFileDialog, QTableWidgetItem, QAbstractItemView,
                             QLabel, QShortcut, QVBoxLayout)
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtGui import QIcon, QKeySequence, QFont
from core import DPlayerCore


class Window(QWidget):
    def __init__(self, title, text):
        """Creates new window with title and text."""
        super().__init__()
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)

        self.isClosed = False
        layout = QVBoxLayout()

        layout.addWidget(label)
        self.setLayout(layout)

        self.setGeometry(300, 300, 500, 500)
        self.setWindowTitle(title)
        self.show()

    def closeEvent(self, event):
        """Closes window."""
        self.isClosed = True
        event.accept()


class DPlayerUI(QWidget):
    def __init__(self):
        """Initializes core and ui"""
        super().__init__()

        self.playerCore = DPlayerCore()
        self.player = self.playerCore.player
        self.playlist = self.playerCore.playlist
        self.initUI()
        self.connectSignals()

    def initUI(self):
        """Initialize user interface - buttons, sliders, labels, playlist."""
        self.grid = QGridLayout()

        self.initButtons()
        self.initVolumeSlider()
        self.initPositionSlider()
        self.initDurationLabel()
        self.initPlaylist()
        self.initSongLabel()

        self.setLayout(self.grid)
        self.setGeometry(0, 0, 700, 700)
        self.setWindowTitle('DPlayer')
        self.setWindowIcon(QIcon('icons/logo.png'))
        self.center()
        self.show()

    def connectSignals(self):
        """Connect player signals to functions."""
        self.player.durationChanged.connect(self.durationChanged)
        self.player.positionChanged.connect(self.positionChanged)
        self.player.stateChanged.connect(self.stateChanged)
        self.player.currentMediaChanged.connect(self.songChanged)

    def initButtons(self):
        """Create, set and connect buttons."""
        self.buttons = {}
        self.buttonNames = ['stop', 'previous', 'play', 'next', 'mute',
                            'addFiles', 'addFolder', 'shuffle',
                            'repeatPlaylist', 'repeatSong', 'Save playlist',
                            'Load playlist', 'Clear playlist', 'Find lyrics',
                            'Find info']
        shortcuts = ['q', 'w', 'e', 'r', 't', 'a', 's', 'd', 'f', 'g', 'z',
                     'x', 'c', 'v', 'b']

        for name, cut in zip(self.buttonNames, shortcuts):
            button = QPushButton(self)
            button.setToolTip(name)
            button.setShortcut(QKeySequence(cut))
            self.buttons[name] = button

        for name in self.buttonNames[:10]:
            self.buttons[name].setIcon(QIcon('icons/{}.png'.format(name)))
            self.buttons[name].setIconSize(QSize(20, 20))

        for name, position in zip(self.buttonNames[:5], range(5)):
            self.grid.addWidget(self.buttons[name], 1, position)

        self.buttons['stop'].clicked.connect(self.stopClicked)
        self.buttons['previous'].clicked.connect(self.previousClicked)
        self.previousButtonClicked = False
        self.buttons['play'].clicked.connect(self.playClicked)
        self.buttons['play'].setFocus()
        self.buttons['next'].clicked.connect(self.nextClicked)
        self.buttons['mute'].clicked.connect(self.muteClicked)
        self.buttons['mute'].setIcon(QIcon('icons/volumeMiddle.png'))

        for name, position in zip(self.buttonNames[5:], range(5)):
            self.grid.addWidget(self.buttons[name], 3, position)

        self.buttons['addFiles'].clicked.connect(self.addFiles)
        self.buttons['addFolder'].clicked.connect(self.addFolder)
        self.buttons['shuffle'].clicked[bool].connect(self.playerCore.shuffle)
        self.buttons['shuffle'].setCheckable(True)
        self.buttons['repeatPlaylist'].clicked[bool].connect(
            self.playerCore.repeatPlaylist)
        self.buttons['repeatPlaylist'].setCheckable(True)
        self.buttons['repeatSong'].clicked[bool].connect(
            self.playerCore.repeatSong)
        self.buttons['repeatSong'].setCheckable(True)

        for name, position in zip(self.buttonNames[10:], range(5)):
            self.buttons[name].setIcon(QIcon('icons/{}.png'.format(name)))
            self.buttons[name].setIconSize(QSize(120, 20))
            self.grid.addWidget(self.buttons[name], 4, position)

        self.buttons['Save playlist'].clicked.connect(self.savePlaylist)
        self.buttons['Load playlist'].clicked.connect(self.loadPlaylist)
        self.buttons['Clear playlist'].clicked.connect(self.clearPlaylist)
        self.buttons['Find lyrics'].clicked.connect(self.findLyrics)
        self.buttons['Find info'].clicked.connect(self.findInfo)

    def previousClicked(self):
        """Play previous song."""
        self.playerCore.songChanged = True
        self.previousButtonClicked = True
        self.playerCore.previous()
        self.stateChanged()

    def stopClicked(self):
        """Stop the player. Set icon to play button."""
        self.playerCore.stop()
        self.buttons['play'].setIcon(QIcon('icons/play.png'))
        self.buttons['play'].setToolTip('play')
        self.songLabel.setText('')

    def playClicked(self):
        """Play / Pause the player. Set icon to play button."""
        if self.player.state() in (QMediaPlayer.StoppedState,
                                   QMediaPlayer.PausedState):
            self.playerCore.play()
            if self.player.state() == QMediaPlayer.PlayingState:
                self.buttons['play'].setIcon(QIcon('icons/pause.png'))
                self.buttons['play'].setToolTip('pause')
        else:   # QMediaPlayer.PlayingState
            self.playerCore.pause()
            self.buttons['play'].setIcon(QIcon('icons/play.png'))
            self.buttons['play'].setToolTip('play')

        self.songLabel.setText('{} - {}'.format(
            self.playlistTable.item(self.currentPlaying, 0).text(),
            self.playlistTable.item(self.currentPlaying, 1).text()))

    def nextClicked(self):
        """Play next song."""
        self.playerCore.next()
        self.stateChanged()

    def muteClicked(self):
        """Mute / Unmute the player. Set volume slider position."""
        if self.playerCore.isMuted():
            self.playerCore.unmute()
            self.volumeChanged(self.currentVolume)
        else:
            self.playerCore.mute()
            self.volumeChanged(0)

    def addFiles(self):
        """Choose files (*.mp3) to add to the playlist."""
        fileNames, _ = QFileDialog.getOpenFileNames(
            self, 'Add songs', filter='Music (*.mp3 *.ogg *.flac *wav)')
        self.playerCore.add(fileNames)
        self.addClicked(fileNames)

    def addFolder(self):
        """Choose folder to add to the playlist."""
        directory = QFileDialog.getExistingDirectory(self, 'Add a folder')
        self.getFromDir(directory)

    def getFromDir(self, directory):
        """Extract files from directory and add them to the playlist."""
        if not directory:
            return

        dirContent = os.listdir(directory)
        fileNames = []
        for file in dirContent:
            path = '{}/{}'.format(directory, file)
            if os.path.isfile(path) and path[len(path) - 4:] == '.mp3':
                fileNames.append(path)
            elif os.path.isdir(path):
                self.getFromDir(path)
        self.playerCore.add(fileNames)
        self.addClicked(fileNames)

    def addClicked(self, fileNames):
        """Fill the playlist with fileNames' info."""
        if fileNames is None:
            return
        self.playlistTable.setSortingEnabled(False)
        songsToAdd = len(fileNames)
        for name, row in zip(fileNames, range(songsToAdd)):
            currentRow = row + self.playlist.mediaCount() - songsToAdd
            self.playlistTable.insertRow(currentRow)

            artist = self.playerCore.getArtist(name)[0]
            title = self.playerCore.getTitle(name)[0]
            album = self.playerCore.getAlbum(name)[0]
            seconds = self.playerCore.getDuration(name)
            duration = QTime(0, seconds // 60, seconds % 60)
            duration = duration.toString('mm:ss')

            rowInfo = [artist, title, album, duration]
            for info, index in zip(rowInfo, range(4)):
                cell = QTableWidgetItem(info)
                self.playlistTable.setItem(currentRow, index, cell)
                font = QFont(info, weight=QFont.Normal)
                cell.setFont(font)
                cell.setTextAlignment(Qt.AlignCenter)
        self.playlistTable.setSortingEnabled(True)

        for index in range(4):
            self.playlistTable.resizeColumnToContents(index)

    def initVolumeSlider(self):
        """Initialize volume slider."""
        self.volumeSlider = QSlider(Qt.Vertical, self)
        self.volumeSlider.setRange(0, 100)
        self.currentVolume = 70
        self.volumeSlider.setValue(self.currentVolume)
        self.volumeSlider.setToolTip('volume: {}'.format(self.currentVolume))
        self.volumeSlider.valueChanged[int].connect(self.volumeChanged)
        self.grid.addWidget(self.volumeSlider, 0, 4, Qt.AlignHCenter)
        self.playerCore.setVolume(self.currentVolume)

    def volumeChanged(self, value):
        """Set player's volume to value. Set icon for sound."""
        self.playerCore.setVolume(value)

        if value == 0:
            self.buttons['mute'].setIcon(QIcon('icons/mute.png'))
        elif value <= 35:
            self.buttons['mute'].setIcon(QIcon('icons/volumeMin.png'))
        elif value <= 70:
            self.buttons['mute'].setIcon(QIcon('icons/volumeMiddle.png'))
        else:   # value <= 100
            self.buttons['mute'].setIcon(QIcon('icons/volumeMax.png'))

        self.volumeSlider.setValue(value)
        self.volumeSlider.setToolTip('volume: {}'.format(value))

        if self.playerCore.isMuted():
            self.buttons['mute'].setToolTip('unmute')
        else:
            self.currentVolume = value
            self.buttons['mute'].setToolTip('mute')

    def initPositionSlider(self):
        """Initialize position slider."""
        self.positionSlider = QSlider(Qt.Horizontal, self)
        self.positionSlider.setValue(0)
        self.positionSlider.valueChanged[int].connect(self.position)
        self.positionSliderClicked = False
        self.grid.addWidget(self.positionSlider, 0, 0, 1, 3, Qt.AlignBottom)

    def initDurationLabel(self):
        """Initialize duration label."""
        self.durationLabel = QLabel('00:00 / 00:00')
        self.grid.addWidget(self.durationLabel, 0, 3, Qt.AlignBottom)

    def durationChanged(self, value):
        """Set the maximum of position slider to value when song is changed."""
        self.positionSlider.setMaximum(value)

    def songChanged(self, _):
        """Handle UI when song changes."""
        if self.doubleClicked or self.playlist.mediaCount() == 0:
            self.doubleClicked = False
            return

        self.lastPlayed = self.currentPlaying
        self.currentPlaying = self.playlist.currentIndex()

        if self.currentPlaying >= 0:
            self.setStyle(self.currentPlaying, QFont.Bold)
            self.songLabel.setText('{} - {}'.format(
                self.playlistTable.item(self.currentPlaying, 0).text(),
                self.playlistTable.item(self.currentPlaying, 1).text()))

        self.playlistTable.scrollToItem(
            self.playlistTable.item(self.currentPlaying, 0))

        if self.lastPlayed >= 0 and self.lastPlayed != self.currentPlaying:
            self.setStyle(self.lastPlayed, QFont.Normal)

        for index in range(4):
            self.playlistTable.resizeColumnToContents(index)

        self.previousButtonClicked = False

    def setStyle(self, row, style):
        """Set row's font to style."""
        for idx in range(4):
                text = self.playlistTable.item(row, idx).text()
                font = QFont(text, weight=style)
                self.playlistTable.item(row, idx).setFont(font)

    def position(self, value):
        """Set the position of player at value."""
        if not self.positionSliderClicked:
            self.positionSliderClicked = True
            self.player.setPosition(value)

    def positionChanged(self, value):
        """Update duration label according to value."""
        if not self.positionSliderClicked:
            self.positionSliderClicked = True
            self.positionSlider.setValue(value)
        self.positionSliderClicked = False

        songIndex = self.playlist.currentIndex()
        if songIndex >= 0:
            duration = self.playlistTable.item(
                self.playlist.currentIndex(), 3).text()
            currentSeconds = value // 1000
            currentTime = QTime(0, currentSeconds // 60, currentSeconds % 60)

            time = '{} / {}'.format(
                currentTime.toString('mm:ss'), duration)
        else:
            time = '00:00 / 00:00'

        self.durationLabel.setText(time)

    def stateChanged(self):
        """Check if stopped to update UI."""
        if self.player.state() == QMediaPlayer.StoppedState:
            self.stopClicked()

    def initSongLabel(self):
        """Initialize song label."""
        self.songLabel = QLabel()
        self.songLabel.setAlignment(Qt.AlignCenter)
        self.font = QFont()
        self.font.setBold(True)
        self.font.setItalic(True)
        self.font.setCapitalization(QFont.AllUppercase)
        self.font.setPixelSize(20)
        self.songLabel.setFont(self.font)
        self.grid.addWidget(self.songLabel, 0, 0, 1, 4, Qt.AlignVCenter)

    def initPlaylist(self):
        """Initialize song playlist."""
        self.playlistTable = QTableWidget()

        self.playlistTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.playlistTable.setSelectionMode(
            QAbstractItemView.ExtendedSelection)
        self.playlistTable.setSortingEnabled(True)

        self.playlistTable.setTabKeyNavigation(False)
        self.playlistTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.playlistTable.setAlternatingRowColors(True)

        self.playlistTable.setVerticalScrollMode(
            QAbstractItemView.ScrollPerPixel)
        self.playlistTable.setHorizontalScrollMode(
            QAbstractItemView.ScrollPerPixel)

        self.playlistTable.itemDoubleClicked.connect(self.doubleClicked)
        self.doubleClicked = False
        self.lastPlayed = -1
        self.currentPlaying = -1
        delete = QShortcut(
            QKeySequence.Delete, self.playlistTable, self.deleteSongs)
        delete.setContext(Qt.WidgetShortcut)

        self.playlistTable.setColumnCount(4)
        self.playlistTable.setHorizontalHeaderLabels(
            ['Artist', 'Title', 'Album', 'Duration'])

        # False - ascending order, True - descending
        self.descendingOrder = [False] * 4
        self.playlistTable.horizontalHeader().sectionClicked.connect(
            self.toSort)

        self.windows = []

        names = []
        for index in range(self.playlist.mediaCount()):
            names.append(self.playlist.media(index).canonicalUrl().path())
        self.addClicked(names)

        self.grid.addWidget(self.playlistTable, 2, 0, 1, 5)
        self.grid.setRowStretch(2, 1)

    def doubleClicked(self, item):
        """Play song at item's row."""
        self.doubleClicked = True
        self.lastPlayed = self.playlist.currentIndex()
        if self.lastPlayed >= 0:
            self.setStyle(self.lastPlayed, QFont.Normal)

        self.currentPlaying = item.row()
        self.playerCore.songChanged = True

        self.playlist.setCurrentIndex(self.currentPlaying)
        self.setStyle(self.currentPlaying, QFont.Bold)
        self.stopClicked()
        self.playClicked()
        self.songLabel.setText('{} - {}'.format(
            self.playlistTable.item(self.currentPlaying, 0).text(),
            self.playlistTable.item(self.currentPlaying, 1).text()))

        for index in range(4):
            self.playlistTable.resizeColumnToContents(index)

    def toSort(self, column):
        """Sort music by column."""
        if self.lastPlayed >= 0:
            self.setStyle(self.lastPlayed, QFont.Normal)
        self.playerCore.sort(column, self.descendingOrder[column])
        self.descendingOrder[column] = bool(1 - self.descendingOrder[column])
        for index in range(4):
            if index != column:
                self.descendingOrder[index] = False

    def deleteSongs(self):
        """Delete selected songs."""
        selectedSongs = self.playlistTable.selectedIndexes()
        indexes = [index.row() for index in selectedSongs]
        toBeRemoved = sorted(indexes[::4], reverse=True)

        currentIndex = self.playlist.currentIndex()
        if currentIndex >= 0:
            self.setStyle(currentIndex, QFont.Normal)

        self.playerCore.remove(toBeRemoved)

        for index in toBeRemoved:
            self.playlistTable.removeRow(index)

        if self.playlistTable.rowCount() == 0:
            return

        currentIndex = self.playlist.currentIndex()
        if currentIndex >= 0:
            self.setStyle(self.playlist.currentIndex(), QFont.Bold)
            self.songLabel.setText('{} - {}'.format(
                self.playlistTable.item(self.currentPlaying, 0).text(),
                self.playlistTable.item(self.currentPlaying, 1).text()))

        for index in range(4):
            self.playlistTable.resizeColumnToContents(index)

    def savePlaylist(self):
        """Save playlist."""
        url, _ = QFileDialog.getSaveFileUrl(self, 'Save playlist')
        self.playerCore.savePlaylist(url)

    def loadPlaylist(self):
        """Load playlist."""
        url, _ = QFileDialog.getOpenFileUrl(
            self, 'Load playlist', filter='Playlists (*.m3u)')

        count = self.playlist.mediaCount()
        self.playerCore.loadPlaylist(url)

        names = []
        for index in range(count, self.playlist.mediaCount()):
            names.append(self.playlist.media(index).canonicalUrl().path())
        self.addClicked(names)

    def clearPlaylist(self):
        """Remove all music from playlist."""
        self.playlistTable.setRowCount(0)
        self.playerCore.clearPlaylist()

    def closeEvent(self, event):
        """Saves current playlist and quits."""
        self.playerCore.savePlaylist(QUrl(
            'file://{}/lastListened.m3u'.format(os.getcwd())))
        event.accept()

    def findLyrics(self):
        """Finds and shows lyrics for selected song(s)."""
        songs = self.playlistTable.selectedIndexes()[::4]
        if not songs:
            return

        for index in songs:
            name = '{} - {}'.format(self.playerCore.musicOrder[index.row()][1],
                                    self.playerCore.musicOrder[index.row()][2])
            lyrics = 'Lyrics:\n\n{}'.format(
                self.playerCore.findLyrics(index.row()))
            self.windows.append(Window(name, lyrics))

        for window in self.windows:
            if window.isClosed:
                self.windows.remove(window)

    def findInfo(self):
        """Opens window with info for selected album at the table."""
        albums = self.playlistTable.selectedIndexes()[::4]
        if not albums:
            return

        for index in albums:
            info = self.playerCore.findInfo(index.row())
            text = '\n'.join(info)
            self.windows.append(Window('Info', text))

    def center(self):
        """Position player application at the center of the screen."""
        # rectangle specifying the geometry of the widget
        rectangle = self.frameGeometry()
        # screen resolution -> center point
        centerPoint = QDesktopWidget().availableGeometry().center()
        # set the center of the rectangle to the center of the screen
        rectangle.moveCenter(centerPoint)
        # move the top-left point of the application window to the top-left
        # point of the rectangle
        self.move(rectangle.topLeft())
