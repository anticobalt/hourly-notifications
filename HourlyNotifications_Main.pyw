# The GUI; all preferences are set here

from tkinter import *
from tkinter import messagebox, simpledialog
from HourlyNotifications_FileHandling import System


def main():
    """
    Create gui from saved settings or default settings
    :return: NoneType
    """
    gui = Interface()
    sounds = System.load_sounds()

    if not sounds:
        gui.warning("Sound files not located. Program will exit.", close=True)
    try:
        settings = System.load_settings()
        choices = settings['choices']
        gui.volume = int(settings['volume'] * 100)
        gui.minute = str(settings['minute']).zfill(2)
    except FileNotFoundError:
        choices = None

    gui.draw_topbar()
    gui.create_selections(sounds, choices)
    gui.run()
    

class Interface:

    def __init__(self):

        self.COLUMN_COUNT = 6
        self.ROW_COUNT = 4

        self._root = Tk()
        self._root.title("Hourly Notifications")
        self._selections = []
        self._topbar = Menu(self._root)
        self._error_handled = []

        self.volume = 20
        self.minute = "00"

    def draw_topbar(self):
        """
        Create top menu bar using tkinter methods
        :return: NoneType
        """
        settings = Menu(self._topbar, tearoff=0)
        debug = Menu(self._topbar, tearoff=0)
        settings.add_command(label="Set Volume", command=self.ask_new_volume)
        settings.add_command(label="Set Minute of the Hour", command=self.ask_new_minute)
        debug.add_command(label="Check for Playback Errors", command=self.check_errors)

        self._topbar.add_cascade(label="Preferences", menu=settings)
        self._topbar.add_cascade(label="Debugging", menu=debug)
        self._topbar.add_command(label="Save", command=self.save)
        self._topbar.add_command(label="Toggle Notifications", command=self.toggle_playback)
        self._root.config(menu=self._topbar)

    def create_selections(self, sounds, saved_choices):
        """
        Increment through rows, columns, and hours to create Selections
        :param sounds: List
        :param saved_choices: Dict
        :return: NoneType
        """
        hour = 0
        for c in range(self.COLUMN_COUNT):
            for r in range(self.ROW_COUNT):
                try:
                    box = Selection(self._root, c, r, hour, self.minute, sounds, saved_choice=saved_choices[hour])
                except:
                    box = Selection(self._root, c, r, hour, self.minute, sounds)
                finally:
                    box.draw_label()
                    box.draw_dropdown()
                hour += 1
                self._selections.append(box)

    def run(self):
        """
        Main program loop
        :return: NoneType
        """
        self._root.resizable(width=False, height=False)
        self._root.mainloop()

    def check_errors(self):
        """
        Uses Sound to check for playback errors
        :return: NoneType
        """
        error = System.load_error()
        if error and (error[0] not in self._error_handled):
            self.warning(error, playback_error=True)
        else:
            self.warning("No new playback errors found.")
            System.save_error(None)

    def ask_new_volume(self):
        """
        Create popup box that lets user change volume percentage
        :return: NoneType
        """
        new_volume = simpledialog.askinteger("Notification Volume", "Set New Volume (1% to 100%)", parent=self._root,
                                             initialvalue=self.volume, minvalue=1, maxvalue=100)
        if new_volume:  # if user didn't cancel
            self.volume = new_volume
            self.save()

    def ask_new_minute(self):
        """
        Create popup box that lets user change what minute every hour notification plays
        :return: NoneType
        """
        new_minute = simpledialog.askinteger("Playback Time", "Set New Minute of the Hour", parent=self._root,
                                             initialvalue=self.minute, minvalue=0, maxvalue=59)
        if new_minute in range(60):  # if user didn't cancel
            self.minute = str(new_minute).zfill(2)
            for box in self._selections:
                box.update_minute(self.minute)
            self.save()

    def save(self):
        """
        Get user choices, save using System, and notify the user save was successful
        :return: NoneType
        """
        selection_values = []
        for selection in self._selections:
            selection_values.append(selection.choice)
        default = Selection.DEFAULT_CHOICE
        System.save_settings(selection_values, default, self.volume, self.minute)
        messagebox.showinfo("Notice", "Settings saved.")

    def warning(self, error, close=False, playback_error=False):
        """
        Generalized warning popup
        :param error: Str or Tuple
        :param close: Bool
        :param playback_error: Bool
        :return: NoneType
        """
        if playback_error:
            self._error_handled.append(error[0])
            if error[1] == UnicodeEncodeError:
                error = "Audio file name contains invalid characters. Rename this hour's file to solve the problem."
            elif error[1] == FileNotFoundError:
                error = error[0] + " does not exist."
        messagebox.showwarning("Error", error)
        if close:
            self._root.destroy()

    def toggle_playback(self):
        """
        Turns playback of notifications on or off
        :return: NoneType
        """
        if System.notifications_on():
            System.control_player(player_on=False, open_player=False)
            message = "Notifications are now OFF."
        else:
            System.control_player(player_on=True, open_player=True)
            message = "Notifications are now ON."
        messagebox.showinfo("Playback Status", message)


class Selection:

    UNIFORM_PADDING = (5, 5)
    LABEL_PADDING = (5, 0)
    DROPDOWN_PADDING = (0, 5)
    DEFAULT_CHOICE = "Choose a sound file"

    def __init__(self, root, time_column, time_row, hour, minute, sounds, saved_choice=None):
        """
        :param root: Tk
        :param time_column: Int
        :param time_row: Int
        :param hour: Int
        :param sounds: List
        :param saved_choice: Str or NoneType
        """
        self._root = root
        self._hour = hour
        self._minute = minute
        self._time_column = time_column
        self._time_row = time_row
        self._saved_choice = saved_choice
        
        # Initialize tkinter objects
        self._label = Text(root, height=1, width=15)
        self._choice = StringVar(self._root)
        self._dropdown = OptionMenu(root, self._choice, *sounds)

    @property
    def choice(self):
        """
        :return: str
        """
        return self._choice.get()

    def draw_label(self):
        """
        Draw text indicating what time's notification can be set in following menu
        :return: NoneType
        """
        self._label.tag_config('center', justify=CENTER)  # creates a tag with name 'center' that can center text
        self._label.insert(END, "Sound for " + str(self._hour) + ":" + self._minute, 'center')

        # Each row of Selection objects actually has two subrows; Tkinter uses these subrows to draw
        self._label.grid(row=self._time_row * 2, column=self._time_column,
                         padx=Selection.UNIFORM_PADDING, pady=Selection.LABEL_PADDING)

    def draw_dropdown(self):
        """
        Draw menu which lets users choose notification for a given time
        :return: NoneType
        """
        if self._saved_choice:
            self._choice.set(self._saved_choice)
        else:
            self._choice.set(Selection.DEFAULT_CHOICE)
        self._dropdown.grid(row=(self._time_row * 2) + 1, column=self._time_column,
                            padx=Selection.UNIFORM_PADDING, pady=Selection.DROPDOWN_PADDING)

    def update_minute(self, minute):
        """
        :param minute: str
        :return: NoneType
        """
        self._minute = minute
        self._label.delete(1.0, END)
        self._label.insert(END, "Sound for " + str(self._hour) + ":" + self._minute, 'center')

main()
