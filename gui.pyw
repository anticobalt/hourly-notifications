# The GUI; all preferences are set here

from tkinter import *
from tkinter import messagebox, simpledialog
from tkinter import ttk
from filehandling import System
from player import Sound  # for sound testing
import time

CURRENT_PROGRAM_VERSION = "Estuary"


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
        self._root.title("Hourly Notifications")
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
        notify_state = Menu(self._top_bar, tearoff=0)
        help_ = Menu(self._top_bar, tearoff=0)

        preferences.add_command(label="Set Volume", command=self.ask_new_volume)
        preferences.add_command(label="Set Minute of the Hour", command=self.ask_new_minute)
        preferences.add_command(label="Set Custom Notification", command=self.ask_custom_notification)
        preferences.add_command(label="Toggle Load on Startup", command=self.toggle_startup)
        notify_state.add_command(label="All", command=self.toggle_all_playback)
        notify_state.add_command(label="Hourlies", command=self.toggle_hourly_playback)
        notify_state.add_command(label="Custom", command=self.toggle_custom_playback)
        help_.add_command(label="Check for Standard Playback Errors", command=self.check_errors)
        help_.add_command(label="Current Notification States", command=self.display_notify_states)
        help_.add_command(label="About", command=self.display_about)

        self._top_bar.add_cascade(label="Change Preferences", menu=preferences)
        self._top_bar.add_command(label="Save Preferences", command=self.save)
        self._top_bar.add_cascade(label="Toggle Notifications", menu=notify_state)
        self._top_bar.add_cascade(label="Help", menu=help_)
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
                box = Selection(self._root, c, r, hour, self.minute, sounds, saved_choice=saved_choices.get(hour),
                                volume=(self.volume / 100))
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
        popup = AdvancedPopup("custom_interval", self._root, "Enter Interval in Minutes (Invalid values default to 0)",
                              self._custom_interval, self._custom_interval_state,
                              ["Reset on standby", "Turn off on standby"])
        popup.build()

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

        # Reboot player
        if System.get_player_on() is True:
            System.control_player(player_on=False)
            time.sleep(2)
            System.control_player(player_on=True, start_new_instance=True)
            messagebox.showinfo("Notice", "Player restarted. Custom notification elapsed time has been reset.")

    def check_errors(self):
        """
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
    def display_notify_states():
        """
        :return: NoneType
        """
        player_on = str(System.get_player_on())
        hourly_on = str(System.get_hourlies_on())
        custom_on = str(System.get_customs_on())
        cu_i = str(System.load_settings()["custom_interval"])
        cu_is = str(System.load_settings()["custom_interval_state"])
        messagebox.showinfo("Current States",
                            "Player On: " + player_on + "\n"
                            "Hourly Notifications On: " + hourly_on + "\n"
                            "Custom Notifications On: " + custom_on + "\n"
                            "Custom Interval Length: " + cu_i + "\n"
                            "Custom Interval State: " + cu_is)

    @staticmethod
    def display_about():
        """
        :return: NoneType
        """
        messagebox.showinfo("About",
                            "Hourly Notifications (Version: " + CURRENT_PROGRAM_VERSION + ")\n"
                            "Website: https://github.com/anticobalt/hourly-notifications/")

    def toggle_all_playback(self, silent=False):
        """
        :return: NoneType
        """
        # Override these two methods' popups
        self.toggle_hourly_playback(silent=True)
        self.toggle_custom_playback(silent=True)

        if not silent:
            if System.get_hourlies_on() is True:
                hourlies = "ON"
            else:
                hourlies = "OFF"
            if System.get_customs_on() is True:
                customs = "ON"
            else:
                customs = "OFF"
            message = "Hourly notifications " + hourlies + ". Custom notifications " + customs
            messagebox.showinfo("Playback Status", message)

    @staticmethod
    def toggle_hourly_playback(silent=False):
        """
        :return: NoneType
        """
        on = System.get_hourlies_on()
        if on:
            System.control_player(hourlies_on=False, start_new_instance=False)
            message = "Hourly notifications are now OFF."
        else:
            System.control_player(hourlies_on=True, start_new_instance=True)
            message = "Hourly notifications are now ON."
        if not silent:
            messagebox.showinfo("Playback Status", message)

    @staticmethod
    def toggle_custom_playback(silent=False):
        """
        :return: NoneType
        """
        on = System.get_customs_on()
        if on:
            System.control_player(customs_on=False, start_new_instance=False)
            message = "Custom notifications are now OFF."
        else:
            System.control_player(customs_on=True, start_new_instance=True)
            message = "Custom notifications are now ON."
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

    UNIFORM_PADDING = (10, 10)
    LABEL_PADDING = (10, 0)
    BUTTON_PADDING = (5, 3)
    DROPDOWN_PADDING = (0, 10)
    DEFAULT_CHOICE = "None"

    def __init__(self, root, time_column, time_row, hour, minute, sounds, saved_choice, volume):
        """
        :param root: Tk
        :param time_column: Int
        :param time_row: Int
        :param hour: Int
        :param sounds: List
        :param saved_choice: Str or NoneType
        :param volume: Float; for play button
        """
        self._root = root
        self._hour = hour
        self._minute = minute
        self._time_column = time_column
        self._time_row = time_row
        self._saved_choice = saved_choice
        self._volume = volume
        self._rows_occupied = 3
        
        # Initialize tkinter objects
        self._label = Text(self._root, height=1, width=15, relief="solid", background="#F0F0F0", font="Calibri")
        self._play_button = Button(self._root, text="Play", command=self._play_test, relief="groove",
                                   font=("Calibri", 10, "bold"))
        self._choice = StringVar(self._root)
        self._dropdown = ttk.Combobox(self._root, textvariable=self._choice, values=sounds, font=("Calibri", 12),
                                      width=10)

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
        self._label.grid(row=self._time_row * self._rows_occupied, column=self._time_column,
                         padx=Selection.UNIFORM_PADDING, pady=Selection.LABEL_PADDING)

    def _draw_play_button(self):
        """
        Draw button that will play associated sound when clicked.
        :return: NoneType
        """
        self._play_button.grid(row=(self._time_row * self._rows_occupied) + 1, column=self._time_column,
                         padx=Selection.UNIFORM_PADDING, pady=Selection.BUTTON_PADDING)

    def _draw_dropdown(self):
        """
        Draw menu which lets users choose notification for a given time
        :return: NoneType
        """
        if self._saved_choice:
            self._choice.set(self._saved_choice)
        else:
            self._choice.set(Selection.DEFAULT_CHOICE)
        self._dropdown.grid(row=(self._time_row * self._rows_occupied) + 2, column=self._time_column,
                            padx=Selection.UNIFORM_PADDING, pady=Selection.DROPDOWN_PADDING)

    def _play_test(self):
        """
        :return: NoneType
        """
        player = Sound()
        folder = System.find_sound_folder()  # folder exists, otherwise error would've be been thrown at program start
        try:
            settings = System.load_settings()
            volume = settings['volume']
        except FileNotFoundError:
            volume = self._volume
        if self.choice == Selection.DEFAULT_CHOICE:
            messagebox.showwarning(title="Playback Error", message="No sound set for this time.")
        else:
            if not player.test(filename=self.choice, folder=folder, volume=volume):
                messagebox.showwarning(title="Playback Error", message="Problem playing file. Check the log file.")

    def build(self):
        """
        :return: NoneType
        """
        self._draw_label()
        self._draw_play_button()
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
