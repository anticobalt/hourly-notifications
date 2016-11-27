# Creates GUI that allows user to change settings, and runs the main script

from tkinter import *
from tkinter import messagebox, simpledialog
from HourlyNotifications_FileHandling import Directory
from HourlyNotifications_Play import Sound


def main():
    """
    Create gui from saved settings or default settings
    :return:
    """
    gui = Interface()
    sounds = Directory.get_sounds()
    if not sounds:
        gui.warning("Sound files not located. Program will exit.", close=True)
    try:
        saved_choices, saved_volume = Directory.get_sound_settings(graphics=True)
        gui.set_saved_volume(saved_volume)
    except FileNotFoundError:
        saved_choices = None
    finally:
        minute = str(Directory.get_time_settings()).zfill(2)
        gui.draw_topbar()
        gui.create_selections(minute, sounds, saved_choices)
        gui.run()
    

class Interface:

    def __init__(self):
        self.root = Tk()
        self.root.title("Hourly Notifications")
        self.selections = []
        self.column_count = 6
        self.row_count = 4
        self.topbar = Menu(self.root)
        self.volume = 20
        self.error_handled = []
        self.minute = "00"

    def draw_topbar(self):
        """
        Create top menu bar using tkinter methods
        :return: NoneType
        """
        settings = Menu(self.topbar, tearoff=0)
        settings.add_command(label="Set Volume", command=self.ask_new_volume)
        settings.add_command(label="Set Minute of the Hour", command=self.ask_new_minute)
        settings.add_command(label="Exit", command=self.root.destroy)
        self.topbar.add_cascade(label="Advanced Settings", menu=settings)
        self.topbar.add_command(label="Save", command=self.save)
        self.root.config(menu=self.topbar)

    def create_selections(self, minute, sounds, saved_choices):
        """
        Increment through rows, columns, and hours to create Selections
        :param minute: str
        :param sounds: list
        :param saved_choices: dict
        :return: NoneType
        """
        hour = 0
        self.minute = minute
        for c in range(self.column_count):
            for r in range(self.row_count):
                try:
                    box = Selection(self.root, c, r, hour, self.minute, sounds, saved_choice=saved_choices[hour])
                except:
                    box = Selection(self.root, c, r, hour, self.minute, sounds)
                hour += 1
                self.selections.append(box)

    def run(self):
        """
        Main program loops
        :return: NoneType
        """
        self.root.resizable(width=False, height=False)
        self.root.after(1000, self.run_script)
        self.root.protocol("WM_DELETE_WINDOW", self.root.iconify)
        self.root.mainloop()

    def run_script(self):
        """
        Uses Sound to check if it is time to play notification, and check for errors
        :return:
        """
        Sound.decide_play()
        error = Sound.get_warning_request()
        if error and (error[0] not in self.error_handled):
            self.warning(error, play_error=True)
        self.root.after(10000, self.run_script)

    def set_saved_volume(self, volume):
        """
        Allow user to see what the volume is currently set to
        :param volume: int
        :return: NoneType
        """
        self.volume = volume

    def ask_new_volume(self):
        """
        Create popup box that lets user change volume percentage
        :return: NoneType
        """
        new_volume = simpledialog.askinteger("Notification Volume", "Set New Volume (1% to 100%)", parent=self.root,
                                              initialvalue=self.volume, minvalue=1, maxvalue=100)
        if new_volume:  # if user didn't cancel
            self.volume = new_volume
            Sound.set_volume(self.volume / 100)
            self.save()

    def ask_new_minute(self):
        """
        Create popup box that lets user change what minute every hour notification plays
        :return: NoneType
        """
        new_minute = simpledialog.askinteger("Playback Time", "Set New Minute of the Hour", parent=self.root,
                                              initialvalue=self.minute, minvalue=0, maxvalue=59)
        if new_minute in range(60):  # if user didn't cancel
            self.minute = str(new_minute).zfill(2)
            Sound.set_minute(new_minute)
            for box in self.selections:
                box.set_minute(self.minute)
            self.save()

    def save(self):
        """
        Get user choices, save using Directory, and notify the user save was successful
        :return: NoneType
        """
        selection_values = []
        for selection in self.selections:
            selection_values.append(selection.get_choice())
        default = Selection.get_default_choice()
        Directory.save_sound_settings(selection_values, default, self.volume)
        Directory.save_time_settings(self.minute)
        messagebox.showinfo("Notice", "Settings saved.")

    def warning(self, error, close=False, play_error=False):
        """
        Generalized popup warning
        :param error: str or tuple
        :param close: bool
        :param play_error: bool
        :return: NoneType
        """
        if play_error:
            self.error_handled.append(error[0])
            if error[1] == UnicodeEncodeError:
                error = "Audio file name contains invalid characters. Rename this hour's file to solve the problem."
            elif error[1] == FileNotFoundError:
                error = error[0] + " does not exist."
        messagebox.showwarning("Error", error)
        if close:
            self.root.destroy()


class Selection:

    uni_padding = (5,5)
    label_padding = (5, 0)
    dropdown_padding = (0, 5)
    default_choice = "Choose a sound file"

    @classmethod
    def get_default_choice(cls):
        """
        :return: str
        """
        return cls.default_choice

    def __init__(self, root, c, r, hour, minute, sounds, saved_choice=None):
        """
        :param root: Tk
        :param c: int
        :param r: int
        :param hour: int
        :param sounds: list
        :param saved_choice: str or NoneType
        """
        self.root = root
        self.hour = hour
        self.minute = minute
        self.c = c
        self.r = r
        self.saved_choice = saved_choice
        
        # initialize tkinter objects
        self.label = Text(root, height=1, width=15)
        self.choice = StringVar(self.root)
        self.dropdown = OptionMenu(root, self.choice, *sounds)

        # draw self
        self.draw_label()
        self.draw_dropdown()

    def draw_label(self):
        """
        Draw text indicating what time's notification can be set in following menu
        :return: NoneType
        """
        self.label.tag_config('center', justify=CENTER)  # creates a tag with name 'center' that can center text
        self.label.insert(END, "Sound for " + str(self.hour) + ":" + self.minute, 'center')

        # Each row of Selection objects actually has two subrows; Tkinter uses these subrows to draw
        self.label.grid(row=self.r * 2, column=self.c,
                        padx=Selection.uni_padding, pady=Selection.label_padding)

    def draw_dropdown(self):
        """
        Draw menu which lets users choose notification for a given time
        :return: NoneType
        """
        if self.saved_choice:
            self.choice.set(self.saved_choice)
        else:
            self.choice.set(Selection.default_choice)
        self.dropdown.grid(row=(self.r * 2) + 1, column=self.c,
                           padx=Selection.uni_padding, pady=Selection.dropdown_padding)
    
    def get_choice(self):
        """
        :return: str
        """
        return self.choice.get()

    def set_minute(self, minute):
        """
        :param minute: str
        :return: NoneType
        """
        self.minute = minute
        self.label.delete(1.0, END)
        self.label.insert(END, "Sound for " + str(self.hour) + ":" + self.minute, 'center')

main()
