# Reads and writes to files and folders

import os
import pickle
import subprocess

OLD_PROGRAM_VERSIONS = ["Affinity"]
CURRENT_PROGRAM_VERSION = "Bauxite"


class System:

    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
    SETTINGS_FILE = os.path.join(CURRENT_DIR, "settings.pkl")
    ERROR_FILE = os.path.join(CURRENT_DIR, "error.pkl")
    SWITCH_FILE = os.path.join(CURRENT_DIR, "ctrl.pkl")
    LOG_FILE = os.path.join(CURRENT_DIR, "log.txt")
    PLAYER_SCRIPT = os.path.join(CURRENT_DIR, "player.pyw")

    sound_folder = None

    @classmethod
    def create_path(cls, folder, file_name):
        """
        :param folder: Str
        :param file_name: Str
        :return: Str
        """
        return os.path.join(folder, file_name)

    @classmethod
    def load_sounds(cls):
        """
        Scan current directory for a sound folder, and scan that sound folder for sound files
        :return: List or NoneType
        """

        # Set initial values
        file_types = ["ogg", "mp3", "flac", "wav"]
        sounds = []

        # Scan for a sound folder
        for obj in os.listdir(cls.CURRENT_DIR):
            sys_path = os.path.join(cls.CURRENT_DIR, obj)
            if os.path.isdir(sys_path) and 'sound' in obj:
                cls.sound_folder = sys_path

        # Create a list of sounds from sound folder
        if cls.sound_folder:
            folder_contents = os.listdir(cls.sound_folder)
            for extension in file_types:
                files = [file_name for file_name in folder_contents if extension in file_name]
                if files:
                    sounds.extend(files)
            return sounds
        else:
            return None

    @classmethod
    def save_settings(cls, values, default, volume, minute):
        """
        Verify sound values, and save by object serialization
        :param values: List
        :param default: Str
        :param volume: Int
        :param minute: Str
        :return: NoneType
        """

        # create dictionary of sounds, discarding non-sound values
        sound_choices = dict()
        for i in range(len(values)):
            if values[i] != default:
                sound_choices[i] = values[i]

        # Sound class requires volume to be float between 0 and 1
        volume /= 100

        # write to save file
        data = dict(folder=cls.sound_folder, choices=sound_choices, volume=volume, minute=minute)
        with open(cls.SETTINGS_FILE, "wb") as f:
            pickle.dump(data, f)

    @classmethod
    def load_settings(cls):
        """
        Load from save file by object deserialization
        :return: Dict or Exception; Dict has the keys "folder", "choices", "volume", and "minute"
            :folder: Str
            :choices: List of Str
            :volume: Float
            :minute: Str
        """

        try:
            with open(cls.SETTINGS_FILE, "rb") as f:
                settings = pickle.load(f)
            return settings
        except FileNotFoundError:
            # reached when save file is incomplete or non-existent
            raise

    @classmethod
    def save_error(cls, error):
        """
        :param error: Tuple
        :return: NoneType
        """
        with open(cls.ERROR_FILE, "wb") as f:
            pickle.dump(error, f)

    @classmethod
    def load_error(cls):
        """
        :return: Tuple or NoneType
        """
        try:
            with open(cls.ERROR_FILE, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return None

    @classmethod
    def control_player(cls, player_on=True, open_player=False):
        """
        :param player_on: Bool
        :param open_player: Bool
        :return: NoneType
        """
        with open(cls.SWITCH_FILE, "wb") as f:
            pickle.dump(player_on, f)
        if open_player:
            subprocess.Popen(["python", cls.PLAYER_SCRIPT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             creationflags=0x08000000)

    @classmethod
    def notifications_on(cls):
        """
        Used by GUI to determine if player is running; used by player to determine if it's supposed to be running
        :return: Bool
        """
        try:
            with open(cls.SWITCH_FILE, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return False

    @classmethod
    def write_log(cls, log):
        """
        :param log: Str
        :return: NoneType
        """
        with open(cls.LOG_FILE, "a") as f:
            f.write(log + "\n")

    @classmethod
    def convert_preferences(cls):
        """
        :return: Bool; True if converted, False otherwise
        """
        affinity_preferences = [os.path.join(cls.CURRENT_DIR, "soundsettings.pkl"),
                                os.path.join(cls.CURRENT_DIR, "timesettings.pkl")]

        if os.path.exists(affinity_preferences[0]):
            with open(affinity_preferences[0], "rb") as f:
                sound_folder, sound_choices, volume = pickle.load(f)
            with open(affinity_preferences[1], "rb") as f:
                minute = pickle.load(f)
            with open(cls.SETTINGS_FILE, "wb") as f:
                pickle.dump(dict(folder=sound_folder, choices=sound_choices, volume=volume, minute=minute), f)
            for file in affinity_preferences:
                os.remove(file)
            return True
        else:
            return False
