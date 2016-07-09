import os
import requests
from operator import itemgetter
from PyQt5.QtCore import QUrl, QFileInfo, QTime
from PyQt5.QtWidgets import QWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from pydub.utils import mediainfo
import pylast


class DPlayerCore(QWidget):
    def __init__(self):
        """Initialize player and load playlist if any."""
        super().__init__()

        self.player = QMediaPlayer()
        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)

        self.shuffling = False
        self.repeatingPlaylist = False
        self.repeatingSong = False

        self.musicOrder = []
        self.loadPlaylist(QUrl(
            'file://{}/lastListened.m3u'.format(os.getcwd())))

        self.lyricsApi = 'http://api.musixmatch.com/ws/1.1/'
        self.lyricsApiKey = '4b364f0652e471aa50813a22cdf830ea'
        self.lastFMapi = 'http://ws.audioscrobbler.com/2.0/'
        self.lastFMapikey = '052c43a00a4fc294bb3c9e0c38bdf710'
        self.lastFMsecret = '14c66392fa9c6c142a41ccc2b0674e19'
        self.username = None
        self.password = None
        self.network = None
        self.error = 'Something went wrong! Try again later.'

    def play(self):
        """Start the player."""
        self.player.play()

    def pause(self):
        """Pause the player."""
        self.player.pause()

    def stop(self):
        """Stop the player."""
        self.player.stop()

    def previous(self):
        """Play previous song."""
        self.playlist.previous()

    def next(self):
        """Play next song."""
        self.playlist.next()

    def mute(self):
        """Mute the player."""
        self.player.setMuted(True)

    def unmute(self):
        """Unmute the player."""
        self.player.setMuted(False)

    def setVolume(self, value):
        """Set player's volume to value."""
        self.player.setVolume(value)

    def add(self, fileNames):
        """Add fileNames to the playlist."""
        for name in fileNames:
            url = QUrl.fromLocalFile(QFileInfo(name).absoluteFilePath())
            self.playlist.addMedia(QMediaContent(url))
            self.musicOrder.append([name])

        self.added(len(fileNames))

    def added(self, added):
        """Saves music info in musicOrder."""
        for name, index in zip(
                self.musicOrder[self.playlist.mediaCount() - added:],
                range(self.playlist.mediaCount() - added,
                      len(self.musicOrder))):
            name = name[0]
            artist = self.getArtist(name)[0]
            title = self.getTitle(name)[0]
            album = self.getAlbum(name)[0]
            seconds = self.getDuration(name)
            duration = QTime(0, seconds // 60, seconds % 60)
            duration = duration.toString('mm:ss')
            self.musicOrder[index].extend(
                [artist, title, album, duration])

    def remove(self, songIndexes):
        """Remove songIndexes from the playlist."""
        for index in songIndexes:
            self.songChanged = True
            del self.musicOrder[index]
            self.playlist.removeMedia(index)
        self.songChanged = False

    def savePlaylist(self, path):
        """Save playlist to path."""
        if path.toString()[len(path.toString()) - 4:] != '.m3u':
            path = QUrl('{}.m3u'.format(path.toString()))
        self.playlist.save(path, 'm3u')

    def loadPlaylist(self, path):
        """Load playlist form path."""
        count = self.playlist.mediaCount()
        self.playlist.load(path)

        for index in range(count, self.playlist.mediaCount()):
            self.musicOrder.append(
                [self.playlist.media(index).canonicalUrl().path()])

        self.added(self.playlist.mediaCount() - count)

    def clearPlaylist(self):
        """Delete all songs in the playlist."""
        self.playlist.clear()
        self.musicOrder = []

    def shuffle(self, value):
        """Shuffle playlist if value = True."""
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
        """Repeat playlist after the last song is finished if value = True."""
        self.repeatingPlaylist = value

        if self.repeatingSong or self.shuffling:
            return
        if self.repeatingPlaylist:
            self.playlist.setPlaybackMode(QMediaPlaylist.Loop)
        else:
            self.playlist.setPlaybackMode(QMediaPlaylist.Sequential)

    def repeatSong(self, value):
        """Repeat current song if value = True."""
        self.repeatingSong = value

        if self.repeatingSong:
            self.playlist.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
        elif self.shuffling:
            self.playlist.setPlaybackMode(QMediaPlaylist.Random)
        elif self.repeatingPlaylist:
            self.playlist.setPlaybackMode(QMediaPlaylist.Loop)
        else:
            self.playlist.setPlaybackMode(QMediaPlaylist.Sequential)

    def sort(self, column, order):
        """Sort playlist by column in order."""
        ordered = sorted(self.musicOrder, key=itemgetter(column + 1),
                         reverse=order)

        self.clearPlaylist()
        for song in ordered:
            url = QUrl.fromLocalFile(QFileInfo(song[0]).absoluteFilePath())
            self.playlist.addMedia(QMediaContent(url))

        self.musicOrder = ordered

    def findLyrics(self, index):
        """Returns lyrics for song at index."""
        if self.musicOrder[index][2] == 'Unknown':
            return 'Unknown song.'

        searchSong = '{}track.search?q_track={}'.format(
            self.lyricsApi, self.musicOrder[index][2].replace(' ', '%20'))
        if self.musicOrder[index][1] != 'Unknown':
            searchSong = '{}&q_artist={}'.format(
                searchSong, self.musicOrder[index][1].replace(' ', '%20'))
        searchSong = '{}&f_has_lyrics=1&apikey={}'.format(
            searchSong, self.lyricsApiKey)

        try:
            requestSong = requests.get(searchSong)
        except requests.ConnectionError:
            return self.error

        songJson = requestSong.json()
        if requestSong.status_code != 200 or \
                songJson['message']['header']['available'] == 0:
            return self.error

        songId = songJson[
            'message']['body']['track_list'][0]["track"]["track_id"]
        searchLyrics = '{}track.lyrics.get?track_id={}&apikey={}'.format(
            self.lyricsApi, songId, self.lyricsApiKey)

        try:
            requestLyrics = requests.get(searchLyrics)
        except requests.ConnectionError:
            return self.error

        if requestLyrics.status_code != 200 or \
                songJson['message']['header']['available'] == 0:
            return self.error
        return requestLyrics.json()[
            'message']['body']['lyrics']['lyrics_body'][:-58]  # spam and bacon

    def findInfo(self, index):
        """Returns info about artist and album for index if any."""
        info = []

        if self.musicOrder[index][1] != 'Unknown':
            artist = self.artistInfo(self.musicOrder[index][1])
            if artist != self.error:
                info += artist

        if self.musicOrder[index][1] != 'Unknown' and \
                self.musicOrder[index][3] != 'Unknown':
            album = self.albumInfo(self.musicOrder[index][1],
                                   self.musicOrder[index][3])
            if album != self.error:
                info += album

        if info:
            return info
        else:
            return ['Unknown artist and song!']

    def artistInfo(self, artist):
        """Returns info about artist if any."""
        try:
            response = requests.get(
                ('{}/?method=artist.getinfo&artist={}&api_key={}&'
                    'format=json&autocorrect=1').format(
                    self.lastFMapi, artist, self.lastFMapikey))
        except Exception:
            return self.error

        if response.status_code != 200:
            return self.error

        artist = 'Artist: {}'.format(response.json()['artist']['name'])
        bio = 'Bio: {}'.format(
            response.json()['artist']['bio']['summary'].replace('.', '.\n'))
        spam = bio.find('<a')
        bio = bio[:spam]

        return [artist, bio]

    def albumInfo(self, artist, album):
        """Returns info about album if any."""
        try:
            response = requests.get(
                ('{}/?method=album.getinfo&artist={}&album={}&api_key={}&'
                    'format=json&autocorrect=1').format(
                    self.lastFMapi, artist, album, self.lastFMapikey))
        except Exception:
            return self.error

        if response.status_code != 200 or \
                'album' not in response.json().keys():
            return self.error

        album = 'Album: {}'.format(response.json()['album']['name'])
        tracks = ['Tracks: ']
        t = response.json()['album']['tracks']['track']
        for track, index in zip(t, range(len(t))):
            tracks.append('{}. {}'.format(index + 1, track['name']))

        info = [album, '\n'.join(tracks)]

        if 'wiki' in response.json()['album'].keys():
            wiki = response.json()['album']['wiki']
            if 'published' in wiki.keys():
                info.append('Published: {}'.format(wiki['published']))
            if 'summary' in wiki.keys():
                summary = wiki['summary'].replace('.', '.\n')
                spam = summary.find('<a')
                info.append('Summary: {}'.format(summary[:spam]))
            if 'Musical style' in wiki.keys():
                info.append('Musical style: {}'.format(wiki['Musical style']))

        return info

    def login(self, username, password):
        """Creates lastFM network."""
        self.username = username
        self.password = pylast.md5(password)
        try:
            self.network = pylast.LastFMNetwork(api_key=self.lastFMapikey,
                                                api_secret=self.lastFMsecret,
                                                username=self.username,
                                                password_hash=self.password)
        except Exception:
            self.username = None
            self.password = None
            self.network = None
            return False
        return True

    def logout(self):
        """Destoys lastFM network and current user info."""
        self.username = None
        self.password = None
        self.network = None

    def loveTrack(self, index):
        """Love track at index in lastFM."""
        if self.network is None:
            return False

        track = self.network.get_track(self.musicOrder[index][1],
                                       self.musicOrder[index][2])
        try:
            track.love()
        except Exception:
            return False
        return True

    def unloveTrack(self, index):
        """Unlove track at index in lastFM."""
        if self.network is None:
            return False

        track = self.network.get_track(self.musicOrder[index][1],
                                       self.musicOrder[index][2])
        try:
            track.unlove()
        except Exception:
            return False
        return True

    def isMuted(self):
        """Returns True if player is muted."""
        return self.player.isMuted()

    def getArtist(self, song):
        """Returns the artist of song."""
        if song[-4:] == '.mp3':
            obj = EasyID3(song)
            if 'artist' in obj.keys():
                return obj['artist']
        elif 'TAG' in mediainfo(song).keys():
            obj = mediainfo(song)['TAG']
            if 'artist' in obj.keys():
                return [obj['artist']]
            elif 'ARTIST' in obj.keys():
                return [obj['ARTIST']]
            else:
                return ['Unknown']
        else:
            return ['Unknown']

    def getTitle(self, song):
        """Returns the title of song."""
        if song[-4:] == '.mp3':
            obj = EasyID3(song)
            if 'title' in obj.keys():
                return obj['title']
        elif 'TAG' in mediainfo(song).keys():
            obj = mediainfo(song)['TAG']
            if 'title' in obj.keys():
                return [obj['title']]
            elif 'TITLE' in obj.keys():
                return [obj['TITLE']]
            else:
                return ['Unknown']
        else:
            return ['Unknown']

    def getAlbum(self, song):
        """Returns the album of song."""
        if song[-4:] == '.mp3':
            obj = EasyID3(song)
            if 'album' in obj.keys():
                return obj['album']
        elif 'TAG' in mediainfo(song).keys():
            obj = mediainfo(song)['TAG']
            if 'album' in obj.keys():
                return [obj['album']]
            elif 'ALBUM' in obj.keys():
                return [obj['ALBUM']]
            else:
                return ['Unknown']
        else:
            return ['Unknown']

    def getDuration(self, song):
        """Returns the duration of song."""
        if song[-4:] == '.mp3':
            return MP3(song).info.length
        return int(float(mediainfo(song)['duration']))
