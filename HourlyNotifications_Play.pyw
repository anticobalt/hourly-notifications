# Checks time and plays audio

from HourlyNotifications_FileHandling import System
import pyglet
import time
from datetime import datetime as d, time as t


def main():
    player = Sound()
    while 1:
        try:
            player.decide_play()
        except Exception as e:
            System.write_log(str(e))
        System.write_log("\n".join(player.log))
        for i in range(10):
            time.sleep(1)
            if System.player_off():
                break
        else:  # executed if loop completes
            continue
        break  # executed if loop is broken out of


class Sound:

    def __init__(self):
        self.hour_last_played = None
        self.log = []

    def decide_play(self):
        """
        Checks if it is time to play a sound
        :return: NoneType
        """
        self.log = []
        system_time = d.now().time()
        self.log.append(str(system_time))
        minute = int(System.load_settings(gui=False)[3])
        
        for hour in range(24):
            if (self.hour_last_played != hour) and (t(hour, minute) <= system_time <= t(hour, minute+1)):
                # play sound if sound has not been played in the last hour, and it is the appropriate time
                if self.play_sound(hour):
                    self.hour_last_played = hour
                    self.log.append(str(hour) + " played; " + str(self.hour_last_played) + " last played.")

    def play_sound(self, hour):
        """
        Tries to play a sound
        :param hour: int
        :return: bool
        """
        try:
            folder, sounds, volume, minute = System.load_settings(gui=False)
            file_name = sounds[hour]
            file = System.create_path(folder, file_name)
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
            System.save_error(error)
        except pyglet.media.avbin.AVbinException:
            error = (file, FileNotFoundError)
            System.save_error(error)

if __name__ == "__main__":
    main()
