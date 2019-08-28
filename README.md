# hourly-notifications

Tested on Windows 10 (probably works on 7/8). Requires Python3.

![Screenshot](https://vgy.me/VbG6bC.png)

### Main Features
- Plays mp3/ogg/flac files in the background
- Comes with GUI that lets you:
	- Set hourly alarms
	- Set alarms for a custom interval (e.g. every 42 minutes)
	- Change the number of minutes into an hour alarms play at (e.g. quarter past every hour, instead of on the hour)
	- Listen to files on-demand
	- Set simple profiles that read files from a folder and infers which file should be set to which hour

### How to Use
1. `pip install -r requirements.txt`
2. In the program's folder, make a folder named 'sounds'. This new folder should contain sounds you want to use.
3. In the 'sounds' folder, create a folder called 'alt' and put as many sound files for the custom alarm in here as you want. When it is time for the alarm to sound, a random file will be chosen to play.
4. Open `gui.pyw` with Python3 to manage and turn notifications on/off

### Advanced Usage: Profiles
-  Make a subfolder inside the 'sounds' folder to add a set of files for a profile. Active profile can be set by name in the GUI, where the name is the name of the folder.
-  Any files not in a subfolder (directly inside 'sounds') belong to the default profile, which is a profile with no name.
 - The GUI will try to automatically set files to hours based on file name. In order of priority, it will match `my_file_nameXX.extension` or `my_file_nameXXXX.extension`, where `XX` is a two-digit time (e.g. 14 for 2PM), `XXXX` is four-digit (e.g. 1400 for 2PM), and `extension` is a support file type. If no pattern can be matched for 24 files, default file order is used (typically alphabetical).

## License
Program is licensed under [MIT](LICENSE).