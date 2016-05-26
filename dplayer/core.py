from PyQt5.QtCore import QUrl, QFileInfo
from PyQt5.QtWidgets import QWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent


class DPlayerCore(QWidget):
    def __init__(self):
        super().__init__()

        self.player = QMediaPlayer()
        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()

    def mute(self):
        self.player.setMuted(True)

    def unmute(self):
        self.player.setMuted(False)

    def previous(self):
        self.playlist.previous()

    def next(self):
        self.playlist.next()

    def volume(self, value):
        self.player.setVolume(value)

    def add(self, fileNames):
        for name in fileNames:
            url = QUrl.fromLocalFile(QFileInfo(name).absoluteFilePath())
            self.playlist.addMedia(QMediaContent(url))

    def state(self):
        return self.player.state()

    def isMuted(self):
        return self.player.isMuted()
