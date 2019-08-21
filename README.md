# hourly-notifications

Tested on Windows 10 (probably works on 7/8). Requires Python3.

![Screenshot](https://vgy.me/VbG6bC.png)

### Main Features
- Plays mp3/ogg/flac files in background
- Comes with GUI that lets you:
	- Set hourly alarms
	- Set alarms for a custom interval (e.g. every 42 minutes)
	- Change the number of minutes into an hour alarms play at (e.g. quarter past every hour, instead of on the hour)
	- Listen to files on-demand

### How to Use
1. `pip install -r requirements.txt`
2. In the program's folder, make a folder named 'sounds'. This new folder should contain sounds you want to use.
3. In the 'sounds' folder, create a folder called 'alt' and put as many sound files for the custom alarm in here as you want. When it is time for the alarm to sound, a random file will be chosen to play.

## License
Program is licensed under [MIT](LICENSE).