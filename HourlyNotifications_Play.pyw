# Checks time and plays audio

from HourlyNotifications_FileHandling import System
from datetime import datetime as d, time as t
import pyglet
import time

CURRENT_PROGRAM_VERSION = "Bauxite"


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
            if not System.notifications_on():
                break
        else:  # executed if loop completes
            continue
        break  # executed if loop is broken out of


class Sound:

    def __init__(self):
        self.hour_last_played = None
        self.log = []
        self.settings = {}

    def decide_play(self):
        """
        Checks if it is time to play a sound
        :return: NoneType
        """
        self.log = []
        system_time = d.now().time()
        self.log.append(str(system_time))
        self.settings = System.load_settings()
        minute = int(self.settings['minute'])
        
        for hour in range(24):
            if (self.hour_last_played != hour) and (t(hour, minute) <= system_time <= t(hour, minute+1)):
                # play sound if sound has not been played in the last hour, and it is the appropriate time
                if self.play_sound(hour):
                    self.hour_last_played = hour
                    self.log.append(str(hour) + " played; " + str(self.hour_last_played) + " last played.")

    def play_sound(self, hour):
        """
        Tries to play a sound
        :param hour: Int
        :return: Bool
        """
        try:
            file_name = self.settings['choices'][hour]
            file = System.create_path(self.settings['folder'], file_name)
            audio = pyglet.media.load(file)
            player = pyglet.media.Player()
            player.queue(audio)
            player.volume = self.settings['volume']
            player.play()
            return True
        except KeyError:
            return False
        except UnicodeEncodeError:  # will be raised even if file doesn't exist to start with
            error = (file, UnicodeEncodeError)
            System.save_error(error)
            return False
        except pyglet.media.avbin.AVbinException:
            error = (file, FileNotFoundError)
            System.save_error(error)
            return False

if __name__ == "__main__":
    System.control_player(player_on=True)
    main()
