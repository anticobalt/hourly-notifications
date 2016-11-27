# Checks time and plays audio

import pyglet
from HourlyNotifications_FileHandling import Directory
from datetime import datetime, time


class Sound:

    hour_last_played = None
    volume = 765
    error = None
    minute = 0

    @classmethod
    def decide_play(cls):
        """
        Checks if it is time to play a sound
        :return: NoneType
        """
        system_time = datetime.now().time()
        print(system_time)
        cls.minute = int(Directory.get_time_settings())
        for hour in range(24):
            if (cls.hour_last_played != hour) and (time(hour, cls.minute) <= system_time <= time(hour, cls.minute+5)):
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
            folder, sounds, cls.volume = Directory.get_sound_settings(graphics=False)
            file_name = sounds[hour]
            file = Directory.get_file_path(folder, file_name)
            audio = pyglet.media.load(file)
            player = pyglet.media.Player()
            player.queue(audio)
            player.volume = cls.volume
            player.play()
            return True
        except KeyError:
            return False
        except UnicodeEncodeError:  # will be raised even if file doesn't exist
            cls.error = (file, UnicodeEncodeError)
        except pyglet.media.avbin.AVbinException:
            cls.error = (file, FileNotFoundError)

    @classmethod
    def set_volume(cls, volume):
        """
        :param volume: float
        :return: NoneType
        """
        cls.volume = volume

    @classmethod
    def set_minute(cls, minute):
        """
        :param volume: float
        :return: NoneType
        """
        cls.minute = minute

    @classmethod
    def get_warning_request(cls):
        """
        :return: Exception
        """
        return cls.error
