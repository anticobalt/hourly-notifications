# Checks time and plays audio

from HourlyNotifications_FileHandling import Directory
from datetime import datetime, time
import pyglet


class Sound:

    hour_last_played = None
    volume = 765

    @classmethod
    def decide_play(cls):
        """
        Checks if it is time to play a sound
        :return: NoneType
        """
        system_time = datetime.now().time()
        print(system_time)
        for hour in range(24):
            if (cls.hour_last_played != hour) and (time(hour, 0) <= system_time <= time(hour, 10)):
                # play sound if sound has not been played in the last hour, and it is the appropriate time
                if cls.play_sound(hour):
                    cls.hour_last_played = hour

    @classmethod
    def play_sound(cls, hour):
        """
        Tries to play a sound
        :param hour: int
        :return: bool
        """
        try:
            folder, sounds, cls.volume = Directory.get_settings(graphics=False)
            file_name = sounds[hour]
            file = Directory.get_file_path(folder, file_name)
            audio = pyglet.media.load(file)
            player = pyglet.media.Player()
            player.queue(audio)
            player.volume = cls.volume
            player.play()
            return True
        except FileNotFoundError:
            return False
        except KeyError:
            return False

    @classmethod
    def set_volume(cls, volume):
        """
        :param volume: float
        :return: NoneType
        """
        cls.volume = volume
