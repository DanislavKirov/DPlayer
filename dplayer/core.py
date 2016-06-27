from PyQt5.QtCore import QUrl, QFileInfo
from PyQt5.QtWidgets import QWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
# from mutagen import wavpack


class DPlayerCore(QWidget):
    def __init__(self):
        super().__init__()

        self.player = QMediaPlayer()
        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)

        self.shuffling = False
        self.repeatingPlaylist = False
        self.repeatingSong = False

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

    def shuffle(self, value):
        self.shuffling = value

        if self.repeatingSong:
            return
        if self.shuffling:
            self.playlist.setPlaybackMode(QMediaPlaylist.Random)
        elif self.repeatingPlaylist:
            self.playlist.setPlaybackMode(QMediaPlaylist.Loop)
        else:
            self.playlist.setPlaybackMode(QMediaPlaylist.Sequential)

    def repeatPlaylist(self, value):
        self.repeatingPlaylist = value

        if self.repeatingSong or self.shuffling:
            return
        if self.repeatingPlaylist:
            self.playlist.setPlaybackMode(QMediaPlaylist.Loop)
        else:
            self.playlist.setPlaybackMode(QMediaPlaylist.Sequential)

    def repeatSong(self, value):
        self.repeatingSong = value

        if self.repeatingSong:
            self.playlist.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
        elif self.shuffling:
            self.playlist.setPlaybackMode(QMediaPlaylist.Random)
        elif self.repeatingPlaylist:
            self.playlist.setPlaybackMode(QMediaPlaylist.Loop)
        else:
            self.playlist.setPlaybackMode(QMediaPlaylist.Sequential)

    def state(self):
        return self.player.state()

    def isMuted(self):
        return self.player.isMuted()

    def numberOfSongs(self):
        return self.playlist.mediaCount()

    def getArtist(self, song):
        if song[-3:] == 'mp3':
            return EasyID3(song)['artist']
        return ['TODO']

    def getTitle(self, song):
        if song[-3:] == 'mp3':
            return EasyID3(song)['title']
        return ['TODO']

    def getAlbum(self, song):
        if song[-3:] == 'mp3':
            return EasyID3(song)['album']
        return ['TODO']

    def getDuration(self, song):
        if song[-3:] == 'mp3':
            return MP3(song).info.length
        return 42
