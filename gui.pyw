# The GUI; all preferences are set here

from tkinter import *
from tkinter import messagebox, simpledialog
from filehandling import System
import time

CURRENT_PROGRAM_VERSION = "Conundrum"


def main():
    """
    Create gui from saved settings or default settings
    :return: NoneType
    """
    gui = MasterWindow()
    gui.all_hourly_sounds = System.load_hourly_sounds()

    if not gui.all_hourly_sounds:
        gui.display_fatal_error("Sound files not located. Program will exit.")
    else:
        try:
            settings = System.load_settings()
            gui.set_preferences(settings)
        except FileNotFoundError:
            pass
        gui.build()
        gui.run()


class MasterWindow:

    save_requested = False

    def __init__(self):

        self.COLUMN_COUNT = 6
        self.ROW_COUNT = 4

        self._root = Tk()
        self._root.title("Hourly Notifications - " + CURRENT_PROGRAM_VERSION)
        self._selections = []
        self._top_bar = Menu(self._root)

        self._volume = [20]
        self._minute = ["00"]
        self._custom_interval = IntVar()
        self._custom_interval.set(0)
        self._custom_interval_state = IntVar()

        self.all_hourly_sounds = []
        self.hourly_sound_choices = dict()

    @property
    def volume(self):
        return self._volume[0]

    @volume.setter
    def volume(self, value):
        self._volume[0] = value

    @property
    def minute(self):
        return self._minute[0]

    @minute.setter
    def minute(self, value):
        self._minute[0] = value

    @property
    def custom_interval(self):
        value = self._custom_interval.get()
        return value

    @custom_interval.setter
    def custom_interval(self, value):
        self._custom_interval.set(value)

    @property
    def custom_interval_state(self):
        value = self._custom_interval_state.get()
        return int(value)

    @custom_interval_state.setter
    def custom_interval_state(self, value):
        self._custom_interval_state.set(value)

    def _ask_attribute_value(self, attribute, prompt_header, prompt_title, min_value, max_value=None,
                             updating_minute=False):
        """
        Generalized prompt that lets user change a numeric preference
        :param attribute: Instance attribute
        :param prompt_header: Str
        :param prompt_title: Str
        :param min_value: Int
        :param max_value: Int or NoneType
        :param updating_minute: Bool
        :return: Bool, representing change (True) or no change (False)
        """
        if max_value is not None:
            new_value = simpledialog.askinteger(prompt_header, prompt_title, parent=self._root,
                                                initialvalue=attribute, minvalue=min_value, maxvalue=max_value)
        else:
            new_value = simpledialog.askinteger(prompt_header, prompt_title, parent=self._root,
                                                initialvalue=attribute, minvalue=min_value)
        if new_value is not None:
            if updating_minute:
                self.minute = str(new_value).zfill(2)
                for box in self._selections:
                    box.update_minute(self.minute)
            else:
                attribute[0] = new_value
            self.save()
            return True
        else:
            return False

    def _warning(self, error, close=False):
        """
        Generalized warning popup
        :param error: Str or Tuple
        :param close: Bool
        :return: NoneType
        """

        if type(error) is tuple:
            error = self._parse_error(error)
        messagebox.showwarning("Error", error)
        if close:
            self._root.destroy()

    def _parse_error(self, error):
        """
        :param error: Tuple or Str
        :return: Str
        """
        problem_file = error[0]
        error_type = error[1]
        if error_type == UnicodeEncodeError:
            error = problem_file + "'s filename contains invalid characters. \n" \
                                   "Rename this file to solve the problem."
        elif error_type == FileNotFoundError:
            error = problem_file + " does not exist."
        elif error_type == ZeroDivisionError:
            error = "File 'avbin.dll' (originally found in c:\windows\system32) is missing from the program directory."
        return error

    def _draw_top_bar(self):
        """
        Create top menu bar using Tkinter methods
        :return: NoneType
        """
        preferences = Menu(self._top_bar, tearoff=0)
        debug = Menu(self._top_bar, tearoff=0)
        preferences.add_command(label="Set Volume", command=self.ask_new_volume)
        preferences.add_command(label="Set Minute of the Hour", command=self.ask_new_minute)
        preferences.add_command(label="Set Custom Notification", command=self.ask_custom_notification)
        preferences.add_command(label="Toggle Load on Startup", command=self.toggle_startup)
        debug.add_command(label="Check for Standard Playback Errors", command=self.check_errors)

        self._top_bar.add_cascade(label="Preferences", menu=preferences)
        self._top_bar.add_cascade(label="Debugging", menu=debug)
        self._top_bar.add_command(label="Save Preferences", command=self.save)
        self._top_bar.add_command(label="Toggle Notifications", command=self.toggle_playback)
        self._root.config(menu=self._top_bar)

    def _create_selections(self, sounds, saved_choices):
        """
        Increment through rows, columns, and hours to create Selections
        :param sounds: List
        :param saved_choices: Dict
        :return: NoneType
        """
        hour = 0
        for c in range(self.COLUMN_COUNT):
            for r in range(self.ROW_COUNT):
                box = Selection(self._root, c, r, hour, self.minute, sounds, saved_choice=saved_choices.get(hour))
                box.build()
                hour += 1
                self._selections.append(box)

    def _handle_requests(self):
        self._handle_save_request()
        self._root.after(1, self._handle_requests)

    def _handle_save_request(self):
        """
        :return: NoneType
        """
        if MasterWindow.save_requested:
            self.save()
            MasterWindow.save_requested = False

    def set_preferences(self, settings):
        self.hourly_sound_choices = settings['choices']
        self.volume = int(settings['volume'] * 100)
        self.minute = settings['minute'].zfill(2)
        self.custom_interval = settings['custom_interval']
        self.custom_interval_state = settings['custom_interval_state']

    def build(self):
        """
        :return: NoneType
        """
        self._draw_top_bar()
        self._create_selections(self.all_hourly_sounds, self.hourly_sound_choices)

    def run(self):
        """
        :return: NoneType
        """
        self._root.resizable(width=False, height=False)
        self._root.after(1, self._handle_requests)
        self._root.mainloop()

    def ask_new_volume(self):
        """
        :return: NoneType
        """
        self._ask_attribute_value(self._volume, "Notification Volume", "Set New Volume (1% to 100%)", 1, 100)

    def ask_new_minute(self):
        """
        :return: NoneType
        """
        self._ask_attribute_value(self._minute, "Playback Time", "Set New Minute of the Hour", 0, 58,
                                  updating_minute=True)

    def ask_custom_notification(self):
        """
        :return: NoneType
        """
        popup = AdvancedPopup("custom_interval", self._root, "Enter Interval in Minutes ('0' for no notification)",
                              self._custom_interval, self._custom_interval_state,
                              ["Reset on standby", "Turn off on standby"])
        popup.build()
        # self._ask_attribute_value(self._mutable_custom_interval, "Custom Notification", "Set Interval in Minutes", 1)

    def save(self):
        """
        :return: NoneType
        """
        selection_values = []
        for selection in self._selections:
            selection_values.append(selection.choice)
        default = Selection.DEFAULT_CHOICE
        System.save_settings(selection_values, default, self.volume, self.minute, self.custom_interval,
                             self.custom_interval_state)
        messagebox.showinfo("Notice", "Applying settings. Give it few seconds.")
        if System.notifications_on():
            self.toggle_playback(silent=True)
            time.sleep(2)
            self.toggle_playback(silent=True)

    def check_errors(self):
        """
        Uses Sound to check for playback errors
        :return: NoneType
        """
        error = System.load_error()
        if error:
            self._warning(error)
            System.save_error(())
        else:
            self._warning("No new playback errors found. If there is a problem, check the log file.\n"
                          "If there's nothing there, restart the player.")

    def display_fatal_error(self, message):
        """
        :return: NoneType
        """
        self._warning(message, close=True)

    @staticmethod
    def toggle_playback(silent=False):
        """
        :return: NoneType
        """
        if System.notifications_on():
            System.control_player(player_on=False, open_player=False)
            message = "Notifications are now OFF."
        else:
            System.control_player(player_on=True, open_player=True)
            message = "Notifications are now ON."
        if not silent:
            messagebox.showinfo("Playback Status", message)

    @staticmethod
    def toggle_startup():
        message = "Explorer will open the location of user startup programs. \n" \
                  "To enable auto-startup, right-click player.pyw in the original program folder to create a " \
                  "shortcut, and move that shortcut into the startup folder that just opened. \n" \
                  "To disable auto-startup, delete the player.pyw shortcut from startup folder."
        messagebox.showinfo("Enable/Disable Auto-Startup of HourlyNotifications", message)
        System.open_startup_folder()


class Selection:

    UNIFORM_PADDING = (5, 5)
    LABEL_PADDING = (5, 0)
    DROPDOWN_PADDING = (0, 5)
    DEFAULT_CHOICE = "Choose a sound file"

    def __init__(self, root, time_column, time_row, hour, minute, sounds, saved_choice):
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
        self._label = Text(self._root, height=1, width=15)
        self._choice = StringVar(self._root)
        self._dropdown = OptionMenu(root, self._choice, *sounds)

    @property
    def choice(self):
        """
        :return: Str
        """
        return self._choice.get()

    def _draw_label(self):
        """
        Draw text indicating what time's notification can be set in following menu
        :return: NoneType
        """
        self._label.tag_config('center', justify=CENTER)  # creates a tag with name 'center' that can center text
        self._label.insert(END, "Sound for " + str(self._hour) + ":" + self._minute, 'center')

        # Each row of Selection objects actually has two subrows; Tkinter uses these subrows to draw
        self._label.grid(row=self._time_row * 2, column=self._time_column,
                         padx=Selection.UNIFORM_PADDING, pady=Selection.LABEL_PADDING)

    def _draw_dropdown(self):
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

    def build(self):
        """
        :return: NoneType
        """
        self._draw_label()
        self._draw_dropdown()

    def update_minute(self, minute):
        """
        :param minute: Str
        :return: NoneType
        """
        self._minute = minute
        self._label.delete(1.0, END)
        self._label.insert(END, "Sound for " + str(self._hour) + ":" + self._minute, 'center')


class AdvancedPopup:

    def __init__(self, preference_name, root, prompt_text, preference_var, rb_state, radio_button_options=[]):
        """
        :param preference_name: Str
        :param root: Tk
        :param prompt_text: Str
        :param preference_var: IntVar
        :param rb_state: IntVar
        :param radio_button_options: List
        """
        self._preference = preference_name
        self._root = root
        self._input_value = preference_var
        self._options = radio_button_options
        self._rb_state = rb_state

        self._window = Toplevel(self._root)
        self._header = Label(self._window, text=prompt_text)
        self._box = Entry(self._window, textvariable=self._input_value, width=20, justify='center')
        self._button = Button(self._window, text="Save", command=self._exit, width=10)

    def _build_window(self):
        """
        :return: NoneType
        """
        root_x = self._root.winfo_x()
        root_y = self._root.winfo_y()
        x_offset = 30
        y_offset = 30

        self._window.geometry("+%d+%d" % (root_x + x_offset, root_y + y_offset))
        self._window.title("Custom Notification")
        self._window.resizable(width=False, height=False)
        # self._window.attributes("-toolwindow", 1)
        self._window.focus()

    def _build_elements(self):
        """
        :return: NoneType
        """
        self._header.grid(padx=20, pady=5, columnspan=2)
        self._box.grid(pady=5, columnspan=2)
        if self._options:
            for index, option in enumerate(self._options):
                rb = Radiobutton(self._window, text=option, value=index, variable=self._rb_state)
                if index % 2 == 0:
                    rb.grid(row=2, column=0, pady=5, sticky=E)
                else:
                    rb.grid(row=2, column=1, pady=5, sticky=W)
        self._button.grid(pady=(5, 10), columnspan=2)

    def _exit(self):
        """
        :return: NoneType
        """
        MasterWindow.save_requested = True
        self._window.destroy()

    def build(self):
        """
        :return: NoneType
        """
        self._build_window()
        self._build_elements()

main()
