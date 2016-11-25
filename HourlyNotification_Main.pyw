# Creates GUI that allows user to change settings, and runs the main script

from tkinter import *
from tkinter import messagebox, simpledialog
from HourlyNotifications_FileHandling import Directory
from HourlyNotifications_Play import Sound


def main():

    gui = Interface()
    sounds = Directory.get_sounds()
    if not sounds:
        gui.alert_missing()
    try:
        saved_choices, saved_volume = Directory.get_settings(graphics=True)
        gui.set_saved_volume(saved_volume)
    except:
        saved_choices = None
    finally:
        gui.draw_topbar()
        gui.create_selections(sounds, saved_choices)
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

    def draw_topbar(self):
        """
        Create top menu bar using tkinter methods
        :return: NoneType
        """
        settings = Menu(self.topbar, tearoff=0)
        settings.add_command(label="Set Volume", command=self.ask_new_volume)
        settings.add_command(label="Exit", command=self.root.destroy)
        self.topbar.add_cascade(label="Advanced Settings", menu=settings)
        self.topbar.add_command(label="Save", command=self.save)
        self.root.config(menu=self.topbar)

    def create_selections(self, sounds, saved_choices):
        """
        Increment through rows, columns, and hours to create Selections
        :param sounds: list
        :param saved_choices: dict
        :return: NoneType
        """
        hour = 0
        for c in range(self.column_count):
            for r in range(self.row_count):
                try:
                    box = Selection(self.root, c, r, hour, sounds, saved_choice=saved_choices[hour])
                except:
                    box = Selection(self.root, c, r, hour, sounds)
                hour += 1
                self.selections.append(box)
    
    def save(self):
        """
        Get user choices, save using Directory, and notify the user save was successful
        :return: NoneType
        """
        selection_values = []
        for selection in self.selections:
            selection_values.append(selection.get_choice())
        default = Selection.get_default_choice()
        Directory.save_settings(selection_values, default, self.volume)
        messagebox.showinfo("Notice", "Settings saved.")

    def alert_missing(self):
        """
        Popup warning for missing audio
        :return: NoneType
        """
        messagebox.showwarning("Error", "Sound files not located. Program will exit.")
        self.root.destroy()

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
        Uses Sound to check if it is time to play notification
        :return:
        """
        Sound.decide_play()
        self.root.after(10000, self.run_script)

    def set_saved_volume(self, volume):
        """
        Allows user to see what the volume is currently set to
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

    def __init__(self, root, c, r, hour, sounds, saved_choice=None):
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
        self.label.insert(END, "Sound for " + str(self.hour) + ":00", 'center')

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


main()
