# Reads and writes to files and folders

import os
import pickle
import subprocess
import random

OLD_PROGRAM_VERSIONS = ["Affinity", "Bauxite", "Conundrum", "Estuary"]
CURRENT_PROGRAM_VERSION = "Frivolity"


class System:

    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
    SETTINGS_FILE = os.path.join(CURRENT_DIR, "settings.pkl")
    BACKUP_SETTINGS_FILE = os.path.join(CURRENT_DIR, "settings_backup.pkl")
    ERROR_FILE = os.path.join(CURRENT_DIR, "error.pkl")
    SWITCH_FILE = os.path.join(CURRENT_DIR, "ctrl.pkl")
    LOG_FILE = os.path.join(CURRENT_DIR, "log.txt")
    PLAYER_SCRIPT = os.path.join(CURRENT_DIR, "player.pyw")

    USER_PROFILE = os.getenv("UserProfile")
    USER_STARTUP_FOLDER = os.path.join(USER_PROFILE, "AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup")

    sound_folder = ""
    alt_sound_folder = ""

    @classmethod
    def _notification_states(cls):
        """
        Used by GUI to determine if player is running; used by player to determine if it's supposed to be running.
        Player is running if hourly notifications, custom notifications, or both are on.
        :return: Dict
        """
        try:
            with open(cls.SWITCH_FILE, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return {"player_on": False,
                    "hourlies_on": False,
                    "customs_on": False}

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
        Scan current directory for a sound folder, and scan that sound folder (recursively) for sound files.
        Ignores the 'alt' folder.
        :return: List of Str; the relative locations of all hourly sounds
        """
        # Set initial values
        file_types = ["ogg", "mp3", "flac"]
        sounds = []
        cls.sound_folder = cls.find_sound_folder()

        # Create a list of sounds from sound folder
        if cls.sound_folder:
            folder_contents = os.listdir(cls.sound_folder)
            for name in folder_contents:
                path = os.path.join(cls.sound_folder, name)
                if 'alt' not in name and os.path.isdir(path):
                    sounds.extend(cls.get_files_recursive(path, file_types))
                else:
                    for extension in file_types:
                        if name.endswith(extension):
                            sounds.append(path)

        return list(map(lambda file_path: os.path.relpath(file_path, cls.sound_folder), sounds))

    @classmethod
    def get_files_recursive(cls, folder_path, file_types):
        """
        Gets files by path that match given types/extensions recursively.
        :param folder_path: Str
        :param file_types: List of Str
        :return: List of Str
        """
        folder_contents = os.listdir(folder_path)
        files = []
        for name in folder_contents:
            path = os.path.join(folder_path, name)
            if os.path.isdir(path):
                files.extend(cls.get_files_recursive(path, file_types))
            else:
                for file_type in file_types:
                    if name.endswith(file_type):
                        files.append(path)
        return files

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
    def save_settings(cls, values, default, volume, minute, profile, custom_interval, custom_interval_state):
        """
        Only called by the GUI
        :param values: List
        :param default: Str
        :param volume: Int
        :param minute: Str
        :param profile: Str
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

        data = dict(version=CURRENT_PROGRAM_VERSION, folder=os.path.join(cls.sound_folder, profile),
                    choices=sound_choices, volume=volume, minute=minute, custom_interval=custom_interval,
                    custom_interval_state=custom_interval_state)
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
    def extract_profile_name(cls, path):
        """
        :param path: Str; full file path to profile folder
        :return: Str; name of profile, or empty string if none exists
        """
        ancestors, child = os.path.split(path)
        if ancestors == cls.sound_folder:
            return child
        else:
            return ""

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
    def control_player(cls, player_on=True, hourlies_on=None, customs_on=None, start_new_instance=False):
        """
        If hourlies_on or custom_on is true/false (i.e. given as arguments), their values in the
        switch file are changed to whatever is given. Otherwise, they are left unaltered.
        
        hourlies_on and custom_on both being false is equivalent to player_on being false.

        :param player_on: Bool. Decides if player actually runs; used by Player
        :param hourlies_on: Bool or NoneType. Used by GUI
        :param customs_on: Bool or NoneType. Used by GUI
        :param start_new_instance: Bool; manual request for new player to start, no matter what
        :return: NoneType
        """
        states = cls._notification_states()
        player_on_currently = states["player_on"]  # is player running right now?
        player_on_later = player_on  # will it run after this method is finished?

        # Decide if player should be on or off by the end of this function
        if (hourlies_on is True) or (customs_on is True):  # arguments are True/True, True/False, or True/None
            player_on_later = True
        elif (hourlies_on is None) or (customs_on is None):  # args are None/None or False/None (True/None prev handled)
            if (states["hourlies_on"] is True and hourlies_on is None) or \
                    (states["customs_on"] is True and customs_on is None):
                player_on_later = True
            else:
                player_on_later = False
        else:  # False/False
            player_on_later = False

        if hourlies_on is not None:
            states["hourlies_on"] = hourlies_on
        if customs_on is not None:
            states["customs_on"] = customs_on

        states["player_on"] = player_on_later
        with open(cls.SWITCH_FILE, "wb") as f:
            pickle.dump(states, f)

        if start_new_instance or (not player_on_currently and player_on_later):
            subprocess.Popen(["python", cls.PLAYER_SCRIPT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             creationflags=0x08000000)

    @classmethod
    def get_player_on(cls):
        """
        :return: Bool
        """
        states = cls._notification_states()
        return states["player_on"]

    @classmethod
    def get_hourlies_on(cls):
        """
        :return: Bool
        """
        states = cls._notification_states()
        return states["hourlies_on"]

    @classmethod
    def get_customs_on(cls):
        """
        :return: Bool
        """
        states = cls._notification_states()
        return states["customs_on"]

    @classmethod
    def open_startup_folder(cls):
        """
        Used by GUI to open startup folder in explorer.
        :return: NoneType
        """
        subprocess.Popen('explorer "' + cls.USER_STARTUP_FOLDER + '"')

    @classmethod
    def write_log(cls, log):
        """
        :param log: Str
        :return: NoneType
        """
        with open(cls.LOG_FILE, "a") as f:
            f.write(log + " PID is " + str(os.getpid()) + ".\n")

    @classmethod
    def convert_preferences(cls):
        """
        :return: Bool; True if converted, False otherwise
        """
        try:
            settings = cls.load_settings()
        except FileNotFoundError:
            return False

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

        elif settings["version"] in ["Conundrum", "Estuary", "Frivolity"]:
            # Placeholder
            return False

        else:
            # This should never be reached
            return False

        cls.save_processed_settings(settings)
        return True
