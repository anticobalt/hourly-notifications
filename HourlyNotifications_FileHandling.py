# Reads and writes to files and folders

import os, pickle, subprocess


class Directory:

    current_folder = os.path.dirname(os.path.realpath(__file__))
    sound_folder = None
    settings_file = os.path.join(current_folder, "settings.pkl")
    log_file = os.path.join(current_folder, "log.pkl")
    ctrl_file = os.path.join(current_folder, "ctrl.pkl")
    player_file = os.path.join(current_folder, "HourlyNotifications_Play.py")

    @classmethod
    def get_file_path(cls, folder, file_name):
        """
        :param folder: str
        :param file_name: str
        :return: str
        """
        return os.path.join(folder, file_name)

    @classmethod
    def get_sounds(cls):
        """
        Scan current directory for a sound folder, and scan that sound folder for sound files
        :return: list or NoneType
        """

        # Set initial values
        file_types = ["ogg", "mp3", "flac", "wav"]
        sounds = []

        # Scan for a sound folder
        for obj in os.listdir(cls.current_folder):
            sys_path = os.path.join(cls.current_folder, obj)
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
        :param values: list
        :param default: str
        :param volume: int
        :param minute: int
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
        with open(cls.settings_file, "wb") as f:
            pickle.dump(data, f)

    @classmethod
    def get_settings(cls, gui=False):
        """
        Load from save file by object deserialization
        :param gui: bool
        :param time: bool
        :return: tuple or error
        """

        try:
            with open(cls.settings_file, "rb") as f:
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
        with open(cls.log_file, "wb") as f:
            pickle.dump(error, f)

    @classmethod
    def get_error(cls):
        """
        :return: Tuple or NoneType
        """
        try:
            with open(cls.log_file, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return None

    @classmethod
    def set_off(cls, off):
        """
        :param off: Bool
        :return: NoneType
        """
        with open(cls.ctrl_file, "wb") as f:
            pickle.dump(off, f)
        if not off:
            subprocess.Popen(["python", cls.player_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    @classmethod
    def player_off(cls):
        """
        Check if player needs to shut off
        :return: Bool
        """
        try:
            with open(cls.ctrl_file, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return False
