# Reads and writes to files and folders

import os
import pickle
import subprocess
import random

OLD_PROGRAM_VERSIONS = ["Affinity", "Bauxite"]
CURRENT_PROGRAM_VERSION = "Conundrum"


class System:

    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
    SETTINGS_FILE = os.path.join(CURRENT_DIR, "settings.pkl")
    BACKUP_SETTINGS_FILE = os.path.join(CURRENT_DIR, "settings_backup.pkl")
    ERROR_FILE = os.path.join(CURRENT_DIR, "error.pkl")
    SWITCH_FILE = os.path.join(CURRENT_DIR, "ctrl.pkl")
    LOG_FILE = os.path.join(CURRENT_DIR, "log.txt")
    PLAYER_SCRIPT = os.path.join(CURRENT_DIR, "player.pyw")

    sound_folder = ""
    alt_sound_folder = ""

    @classmethod
    def create_path(cls, folder, file_name):
        """
        :param folder: Str
        :param file_name: Str
        :return: Str
        """
        return os.path.join(folder, file_name)

    @classmethod
    def find_sound_folder(cls):
        """
        :return: Str
        """
        for obj in os.listdir(cls.CURRENT_DIR):
            sys_path = os.path.join(cls.CURRENT_DIR, obj)
            if os.path.isdir(sys_path) and 'sound' in obj:
                return sys_path
        else:
            return ""

    @classmethod
    def load_hourly_sounds(cls):
        """
        Scan current directory for a sound folder, and scan that sound folder for sound files
        :return: List
        """
        # Set initial values
        file_types = ["ogg", "mp3", "flac", "wav"]
        sounds = []
        cls.sound_folder = cls.find_sound_folder()

        # Create a list of sounds from sound folder
        if cls.sound_folder:
            folder_contents = os.listdir(cls.sound_folder)
            for extension in file_types:
                files = [file_name for file_name in folder_contents if extension in file_name]
                if files:
                    sounds.extend(files)
            return sounds
        else:
            return []

    @classmethod
    def load_alt_sound(cls):
        """
        :return: Str
        """
        cls.sound_folder = cls.find_sound_folder()

        if cls.sound_folder:
            for obj in os.listdir(cls.sound_folder):
                path = os.path.join(cls.sound_folder, obj)
                if os.path.isdir(os.path.join(cls.sound_folder, obj)) and 'alt' in obj:
                    cls.alt_sound_folder = path

        if cls.alt_sound_folder:
            return os.path.join(cls.alt_sound_folder, random.choice(os.listdir(cls.alt_sound_folder)))
        else:
            return ""

    @classmethod
    def save_settings(cls, values, default, volume, minute, custom_interval, custom_interval_state):
        """
        Only called by the GUI
        :param values: List
        :param default: Str
        :param volume: Int
        :param minute: Str
        :param custom_interval: Int
        :param custom_interval_state: Int
        :return: NoneType
        """
        sound_choices = dict()
        for i in range(len(values)):
            if values[i] != default:
                sound_choices[i] = values[i]

        # Sound class requires volume to be float between 0 and 1
        volume /= 100

        data = dict(version=CURRENT_PROGRAM_VERSION, folder=cls.sound_folder, choices=sound_choices, volume=volume,
                    minute=minute, custom_interval=custom_interval, custom_interval_state=custom_interval_state)
        cls.save_processed_settings(data)

    @classmethod
    def save_processed_settings(cls, data):
        """
        :param data: Dict
        :return: NoneType
        """
        with open(cls.SETTINGS_FILE, "wb") as f:
            pickle.dump(data, f)

    @classmethod
    def load_settings(cls):
        """
        :return: Dict or Exception; Dict has the following keys:
            :version: Str
            :folder: Str
            :choices: List of Strings
            :volume: Float
            :minute: Str
            :custom_interval: Int
            :custom_interval_state: Int
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
        :return: Tuple
        """
        try:
            with open(cls.ERROR_FILE, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return ()

    @classmethod
    def valid_file(cls, file, sound_file=False):
        """
        :param file: Str
        :param sound_file: Bool
        :return: Bool
        """
        if sound_file:
            address = os.path.join(cls.sound_folder, file)
        else:
            address = os.path.join(cls.CURRENT_DIR, file)
        return os.path.exists(address)

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
        try:
            settings = cls.load_settings()
        except FileNotFoundError:
            pass

        if os.path.exists(os.path.join(cls.CURRENT_DIR, "soundsettings.pkl")):
            # Affinity
            with open(os.path.join(cls.CURRENT_DIR, "soundsettings.pkl"), "rb") as f:
                sound_folder, sound_choices, volume = pickle.load(f)
            with open(os.path.join(cls.CURRENT_DIR,"timesettings.pkl"), "rb") as f:
                minute = pickle.load(f)
            settings = dict(version=CURRENT_PROGRAM_VERSION, folder=sound_folder, choices=sound_choices, volume=volume,
                            minute=minute, custom_interval=0, custom_interval_state=0)
            if settings["choices"] is None:
                settings["choices"] = dict()

        elif 'version' not in settings:
            # Bauxite
            settings['version'] = CURRENT_PROGRAM_VERSION
            settings['custom_interval'] = 0
            settings['custom_interval_state'] = 0
            if settings["choices"] is None:
                settings["choices"] = dict()
            os.rename(cls.SETTINGS_FILE, cls.BACKUP_SETTINGS_FILE)

        else:
            return False

        cls.save_processed_settings(settings)
        return True
