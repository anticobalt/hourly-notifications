# Checks time and plays audio

from filehandling import System
from datetime import datetime as d, time as t
import pygame
import mutagen
import time
import sys
import traceback

CURRENT_PROGRAM_VERSION = "Frivolity"


def main():
    program = Sound()
    try:
        program.load_settings()
        program.run()
    except FileNotFoundError:
        System.write_log("Save file nonexistent.")
        System.control_player(player_on=False)


class Sound:

    def __init__(self):
        self.run_delay = 10
        self.hour_last_played = None
        self.log = []
        self.settings = dict()
        self.interval = 0  # minutes between each sounding of custom notification
        self.interval_start_time = time.time()
        self.last_handled_time = time.time()

    def load_settings(self):
        self.settings = System.load_settings()
        if isinstance(self.settings['custom_interval'], int) and self.settings['custom_interval'] > 0:
            self.interval = self.settings['custom_interval']

    def run(self):
        while 1:

            self.log = []
            try:
                self.decide_play_hourly()
                self.decide_play_alt()
            except OSError:
                # Resolves [WinError 2005401450] Windows Error 0x88780096 thrown by AudioSwitcher (by @xenolightning)
                System.control_player(player_on=True, start_new_instance=True)
                self.log.append("OS Error Resolved.")
                break
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                exception = traceback.format_exception(exc_type, exc_value, exc_traceback)
                System.write_log("".join(exception))

            if self.log:
                System.write_log("\n".join(self.log))

            for i in range(self.run_delay):
                time.sleep(1)
                if System.get_player_on() is False:
                    break
            else:
                continue
            break

    def decide_play_hourly(self):
        """
        :return: NoneType
        """
        if System.get_hourlies_on() is False:
            return

        system_time = d.now().time()
        minute = int(self.settings['minute'])
        # self.log.append(str(system_time))

        for hour in range(24):
            if (self.hour_last_played != hour) and (t(hour, minute) <= system_time <= t(hour, minute + 1)):
                # play sound if sound has not been played in the last hour, and it is the appropriate time
                try:
                    file_name = self.settings['choices'][hour]
                    file = System.create_path(self.settings['folder'], file_name)
                except KeyError:
                    break
                if self.play_sound(file):
                    self.hour_last_played = hour
                    self.log.append(str(hour) + " played; " + str(self.hour_last_played) + " last played.")
                else:
                    self.log.append(str(hour) + " failed to play; " + str(self.hour_last_played) + " last played.")

    def decide_play_alt(self):
        """
        :return: NoneType
        """
        if System.get_customs_on() is False:
            return

        if self.interval == 0:
            System.control_player(player_on=False)
            return

        state = self.settings['custom_interval_state']
        ctime = time.time()

        if ctime - self.last_handled_time > self.run_delay + 5:
            if state == 0:  # Reset notification interval on system standby (technically, on system wake-up)
                self.interval_start_time = ctime
            elif state == 1:  # Turn off notifications on system standby
                self.interval = 0

        if self.interval and (ctime - self.interval_start_time >= self.interval * 60):
            sound_file_path = System.load_alt_sound()
            if sound_file_path:
                if self.play_sound(sound_file_path):
                    self.log.append(sound_file_path + " played.")
                else:
                    self.log.append(sound_file_path + " failed to play.")
                self.interval_start_time = ctime
            else:
                self.log.append("No alt sounds found.")

        self.log.append(
            str((ctime - self.interval_start_time) / 60) + " minutes since alt sound playback cycle " +
            "started. Time is " + str(d.now().time()) + ". Interval is " + str(self.interval) + "."
        )
        self.last_handled_time = ctime

    """
    Plays sound with PyGame.
    Do NOT initialize PyGame directly, only initialize the mixer, or the sound will not play.
    """

    def play_sound(self, file):
        """
        :param file: Str
        :return: Bool, representing success or failure
        """
        if not System.valid_file(file, sound_file=True):
            error = (file, FileNotFoundError)
        else:
            try:
                # Use sample rate from file, not default, which can distort sound
                sample_rate = mutagen.File(file).info.sample_rate
                pygame.mixer.quit()
                pygame.mixer.init(sample_rate)
                # Play file asynchronously
                pygame.mixer.music.load(file)
                pygame.mixer.music.set_volume(self.settings['volume'])
                pygame.mixer.music.play()
                System.save_error(())
                return True
            except UnicodeEncodeError:
                error = (file, UnicodeEncodeError)
        try:
            System.save_error(error)
        except NameError:
            self.log.append("An unexpected error was encountered.")
        return False

    def test(self, filename, folder, volume):
        """
        Used by GUI to play a sound once
        :param filename: Str
        :param folder: Str
        :param volume: Float (0 to 1)
        :return: Bool
        """
        path = System.create_path(folder, filename)
        self.settings['volume'] = volume
        return self.play_sound(path)


if __name__ == "__main__":
    System.control_player(player_on=True)
    main()
