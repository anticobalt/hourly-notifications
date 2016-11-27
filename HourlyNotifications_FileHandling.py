# Reads and writes to files and folders

import os
import pickle


class Directory:

    current_folder = os.path.dirname(os.path.realpath(__file__))
    sound_folder = None
    script_name = "HourlyNotifications_Play.py"

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
    def save_sound_settings(cls, values, default, volume):
        """
        Verify sound values, and save by object serialization
        :param values: list
        :param default: str
        :param volume: int
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
        data = (cls.sound_folder, sounds, volume)
        location = os.path.join(cls.current_folder, "soundsettings.pkl")
        f = open(location, "wb")
        pickle.dump(data, f)

    @classmethod
    def save_time_settings(cls, minute):
        """
        :param minute: int
        :return: NoneType
        """
        location = os.path.join(cls.current_folder, "timesettings.pkl")
        f = open(location, "wb")
        pickle.dump(minute, f)

    @classmethod
    def get_sound_settings(cls, graphics=True):
        """
        Load from save file by object deserialization
        :param graphics: bool
        :return: tuple or error
        """

        location = os.path.join(cls.current_folder, "soundsettings.pkl")
        try:
            f = open(location, "rb")
            folder, sounds, volume = pickle.load(f)
            if graphics:
                return sounds, int(volume * 100)
            else:
                return folder, sounds, volume
        except FileNotFoundError:
            # reached when save file is incomplete or non-existent
            raise

    @classmethod
    def get_time_settings(cls):
        """
        Try to load save file; if failed, return defaults
        :return: int
        """

        location = os.path.join(cls.current_folder, "timesettings.pkl")
        try:
            f = open(location, "rb")
            return pickle.load(f)
        except FileNotFoundError:
            return 0
