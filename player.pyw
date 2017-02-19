# Checks time and plays audio

from filehandling import System
from datetime import datetime as d, time as t
import pyglet
import time
import sys
import traceback

CURRENT_PROGRAM_VERSION = "Conundrum"


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
        self.interval = 0
        self.interval_start_time = time.time()
        self.last_handled_time = time.time()

    def load_settings(self):
        self.settings = System.load_settings()
        self.interval = self.settings['custom_interval']

    def run(self):
        while 1:
            self.log = []
            try:
                self.decide_play_hourly()
                self.decide_play_alt()
            except OSError:
                # Resolves [WinError 2005401450] Windows Error 0x88780096 thrown by AudioSwitcher (by @xenolightning)
                System.control_player(player_on=True, open_player=True)
                self.log.append("OS Error Resolved.")
                break
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                exception = traceback.format_exception(exc_type, exc_value, exc_traceback)
                System.write_log("".join(exception))
            System.write_log("\n".join(self.log))
            for i in range(self.run_delay):
                time.sleep(1)
                if not System.notifications_on():
                    break
            else:
                continue
            break

    def decide_play_hourly(self):
        """
        :return: NoneType
        """
        system_time = d.now().time()
        minute = int(self.settings['minute'])
        self.log.append(str(system_time))

        for hour in range(24):
            if (self.hour_last_played != hour) and (t(hour, minute) <= system_time <= t(hour, minute+1)):
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

        self.last_handled_time = ctime

    def play_sound(self, file):
        """
        :param file: Str
        :return: Bool, representing success or failure
        """
        if not System.valid_file(file, sound_file=True):
            error = (file, FileNotFoundError)
        elif not System.valid_file("avbin.dll"):
            error = (file, ZeroDivisionError)
        else:
            try:
                audio = pyglet.media.load(file)
                player = pyglet.media.Player()
                player.queue(audio)
                player.volume = self.settings['volume']
                player.play()
                System.save_error(())
                return True
            except UnicodeEncodeError:
                error = (file, UnicodeEncodeError)
        try:
            System.save_error(error)
        except NameError:
            self.log.append("An unexpected error was encountered.")
        return False


if __name__ == "__main__":
    System.control_player(player_on=True)
    main()
