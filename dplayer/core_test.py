import unittest
import core
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
import pylast


class TestCore(unittest.TestCase):
    def setUp(self):
        self.core = core.DPlayerCore()
        self.path = '/home/danislav/python/dplayerenv/dplayer/testing_stuff/'
        self.playlist = ['{}mp3.mp3'.format(self.path),
                         '{}ogg.ogg'.format(self.path),
                         '{}flac.flac'.format(self.path),
                         '{}wav.wav'.format(self.path)]
        self.core.add(self.playlist)
        self.error = 'Something went wrong! Try again later.'

    def test_added(self):
        self.assertEqual(4, self.core.playlist.mediaCount())
        self.assertEqual(self.playlist[0],
                         self.core.musicOrder[0][0])
        self.assertEqual('Godsmack', self.core.musicOrder[0][1])
        self.assertEqual('''Cryin' Like a Bitch''', self.core.musicOrder[0][2])
        self.assertEqual('The Oracle', self.core.musicOrder[0][3])
        self.assertEqual('Unknown', self.core.musicOrder[3][1])
        self.assertEqual('Unknown', self.core.musicOrder[3][2])
        self.assertEqual('Unknown', self.core.musicOrder[3][3])
        self.assertEqual('00:03', self.core.musicOrder[3][4])

    def test_remove(self):
        self.core.remove([1, 2])
        self.assertEqual(2, self.core.playlist.mediaCount())
        self.core.remove([1])
        self.assertEqual(1, self.core.playlist.mediaCount())
        self.assertEqual('Godsmack', self.core.musicOrder[0][1])
        self.core.remove([0])
        self.assertEqual(0, self.core.playlist.mediaCount())

    def test_save_load_clear_playlist(self):
        self.core.savePlaylist(QUrl('file://{}playlist'.format(self.path)))
        self.core.clearPlaylist()
        self.assertEqual(0, self.core.playlist.mediaCount())
        self.core.loadPlaylist(QUrl('file://{}playlist.m3u'.format(self.path)))
        self.assertEqual(4, self.core.playlist.mediaCount())

    def test_sort(self):
        self.core.sort(1, True)
        self.assertEqual(self.playlist[2], self.core.musicOrder[3][0])
        self.assertEqual(self.playlist[3], self.core.musicOrder[0][0])
        self.core.sort(3, False)
        self.assertEqual(self.playlist[0], self.core.musicOrder[3][0])

    def test_lyrics(self):
        self.assertEqual('Unknown song.', self.core.findLyrics(3))

        lyrics = ('Strut on by like a king\n'
                  'Telling everybody they know nothing\n'
                  'And long live what you thought you were\n'
                  'And time ain\'t on your side anymore (anymore)\n'
                  '\n'
                  'And so, you tell me I\n'
                  'Can\'t take my chances\n'
                  'But I told you one too many times\n'
                  'And you were crying like a bitch\n'
                  '\n'
                  'I\'m tougher than nails\n'
                  'I can promise you that\n'
                  'Step out of line\n'
                  'And you get bitch-slapped back\n'
                  'And you can run\n'
                  'Your little mouth all day\n'
                  'But the hand of god\n'
                  'Just smacked you back into yesterday\n')
        self.assertIn(self.core.findLyrics(0), [lyrics, self.error])

    def test_info(self):
        info = ['Artist: Cowboy Junkies',
                ('Bio: The Cowboy Junkies is a Canadian alt-country band '
                    'formed by three siblings from the Timmins entertainment '
                    'family (Margo Timmins, vocals; Michael Timmins, '
                    'songwriter & guitars; Peter Timmins, drums) plus  Alan '
                    'Anton on bass.\n The group formed in Toronto in 1986.\n '
                    'The band\'s name was simply a random choice as they '
                    'approached their first ever gig, but it has come to '
                    'perfectly represent their sound.\n (Some sources may '
                    'credit Townes Van Zandt\'s song "Cowboy Junkies Lament" '
                    'as the source of the band\'s name '),
                'Album: Live at The Ark, 2009-10-05', 'Tracks: ']
        self.assertIn(self.core.findInfo(2),
                      [info, info[:2], info[2:], 'Unknown artist and song.'])

    def test_login(self):
        logged = self.core.login('pylasttest', 'test123456789 ')
        self.assertTrue(logged)
        logged = self.core.login('pylasttest', '')
        self.assertFalse(logged)

    def test_love_unlove(self):
        self.core.login('pylasttest', 'test123456789 ')
        loved = self.core.loveTrack(0)
        if not loved:
            return

        user = pylast.User(self.core.username, self.core.network)
        self.assertEqual(user.get_loved_tracks()[0][0].artist.name, 'Godsmack')

        self.core.unloveTrack(0)
        self.assertEqual(user.get_loved_tracks(), [])

    def tearDown(self):
        self.core.clearPlaylist()
        self.core.logout()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    unittest.main()
    sys.exit(app.exec_())
