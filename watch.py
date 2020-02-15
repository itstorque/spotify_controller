import os
from webbot import Browser
from time import sleep

class SpotifyController:
    def __init__(self):

        self.web = Browser()

        self.web.go_to('https://open.spotify.com/')
        self.web.click('Log in')

        sleep(2)

        auth = open("auth.ctrl","r").read().split("\n")

        self.web.type(auth[0])
        self.web.type(auth[1], into='Password')

        self.web.click('Log in')

        sleep(5)

    def hard_execute(self, text):
        try:
            self.execute(text)
        except:
            print("AAAHHH THE INPUT IS SAD")

    def play(self):
        play_script = "document.querySelectorAll('[data-testid=\"control-button-play\"]')[0].click()"
        self.execute(play_script)

    def pause(self):
        pause_script = "document.querySelectorAll('[data-testid=\"control-button-pause\"]')[0].click()"
        self.execute(pause_script)

    def execute(self, input):
        self.web.execute_script(input)

class SpotifyListener:
    def __init__(self, controller):
        self._cached_stamp = 0
        self.filename = 'sptfy.ctrl'
        self.controller = controller
        self.current_playing = None
        self.lyric_syncer = GeniusLyricSyncer()

    def watch(self):
        stamp = os.stat(self.filename).st_mtime

        self.update()

        if stamp != self._cached_stamp:
            f = open('sptfy.ctrl', 'r+')
            inst = f.read()

            self.decode_function(inst)

            f.truncate(0)
            f.close()
            self._cached_stamp = os.stat(self.filename).st_mtime

    def get_artist_name(self):
        # return self.controller.execute('document.getElementsByClassName("track-info__artists")[0].textContent')

        name = self.controller.web.find_elements(css_selector='.Root__now-playing-bar .now-playing .track-info__artists a')[0].text

        return name

    def get_song_name(self):
        # return self.controller.execute('document.getElementsByClassName("track-info__name")[0].textContent')

        name = self.controller.web.find_elements(css_selector='.Root__now-playing-bar .now-playing .track-info__name a')[0].text

        return name

    def update(self):

        artist_name = self.get_artist_name()

        song_name = self.get_song_name()

        if self.update_current_playing(song_name, artist_name):

            self.lyric_syncer.get_lyrics_link_for_song(song_name, artist_name)

    def update_current_playing(self, song, artist):

        old = self.current_playing

        self.current_playing = (song, artist)

        return old != self.current_playing# True if did actually change

    def decode_function(self, inst):

        if "__pause__" in inst:
            self.controller.pause()
        elif "__play__" in inst:
            self.controller.play()
        elif "__execute__:" in inst:
            self.controller.hard_execute(inst.split("__execute__:")[1])

class GeniusLyricSyncer:

    def __init__(self):
        pass

    def get_lyrics_link_for_song(self, artist, title):
        link = str(artist.lower().capitalize() + " " + title.lower()).replace(" ", "-")
        link = "https://genius.com/" + link + "-lyrics"

        print(link)

        return link

if __name__=="__main__":

    controller = SpotifyController()
    listener = SpotifyListener(controller)

    while True:

        try: listener.watch()
        except Exception as e: print(e)

        sleep(1)
