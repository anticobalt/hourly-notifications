# Checks time and plays audio

from HourlyNotifications_FileHandling import Directory
import pyglet, os, time
from datetime import datetime as d, time as t


def main():
    player = Sound()
    while 1:
        player.decide_play()
        for i in range(10):
            time.sleep(1)
            if Directory.player_off():
                break
        else:  # executed if loop completes
            continue
        break  # executed if loop is broken out of


class Sound:

    def __init__(self):
        self.hour_last_played = None

    def decide_play(self):
        """
        Checks if it is time to play a sound
        :return: NoneType
        """
        system_time = d.now().time()
        minute = int(Directory.get_settings(gui=False)[3])
        for hour in range(24):
            if (self.hour_last_played != hour) and (t(hour, minute) <= system_time <= t(hour, minute+1)):
                # play sound if sound has not been played in the last hour, and it is the appropriate time
                if self.play_sound(hour):
                    self.hour_last_played = hour

    def play_sound(self, hour):
        """
        Tries to play a sound
        :param hour: int
        :return: bool
        """
        try:
            folder, sounds, volume, minute = Directory.get_settings(gui=False)
            file_name = sounds[hour]
            file = Directory.get_file_path(folder, file_name)
            audio = pyglet.media.load(file)
            player = pyglet.media.Player()
            player.queue(audio)
            player.volume = volume
            player.play()
            return True
        except KeyError:
            return False
        except UnicodeEncodeError:  # will be raised even if file doesn't exist to start with
            error = (file, UnicodeEncodeError)
            Directory.save_error(error)
        except pyglet.media.avbin.AVbinException:
            error = (file, FileNotFoundError)
            Directory.save_error(error)

if __name__ == "__main__":
    main()
