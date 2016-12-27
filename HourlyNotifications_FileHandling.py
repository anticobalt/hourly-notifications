# Reads and writes to files and folders

import os, pickle, subprocess


class System:

    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
    SETTINGS_FILE = os.path.join(CURRENT_DIR, "settings.pkl")
    ERROR_FILE = os.path.join(CURRENT_DIR, "error.pkl")
    SWITCH_FILE = os.path.join(CURRENT_DIR, "ctrl.pkl")
    LOG_FILE = os.path.join(CURRENT_DIR, "log.txt")
    PLAYER_SCRIPT = os.path.join(CURRENT_DIR, "HourlyNotifications_Play.pyw")

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
        :param minute: Int
        :return: NoneType
        """

        # create dictionary of sounds, discarding non-sound values
        sounds = dict()
        for i in range(len(values)):
            if values[i] != default:
                sounds[i] = values[i]

        # Sound class requires volume to be float between 0 and 1
        volume /= 100

        # write to save file
        data = (cls.sound_folder, sounds, volume, minute)
        with open(cls.SETTINGS_FILE, "wb") as f:
            pickle.dump(data, f)

    @classmethod
    def load_settings(cls, gui=False):
        """
        Load from save file by object deserialization
        :param gui: Bool
        :return: Tuple or Exception
        """

        try:
            with open(cls.SETTINGS_FILE, "rb") as f:
                folder, sounds, volume, minute = pickle.load(f)
            if gui:
                return sounds, int(volume * 100), minute
            else:
                return folder, sounds, volume, minute
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
    def set_player_off(cls, off):
        """
        :param off: Bool
        :return: NoneType
        """
        with open(cls.SWITCH_FILE, "wb") as f:
            pickle.dump(off, f)
        if not off:
            subprocess.Popen(["python", cls.PLAYER_SCRIPT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             creationflags=0x08000000)

    @classmethod
    def player_off(cls):
        """
        Check if player needs to shut off
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
