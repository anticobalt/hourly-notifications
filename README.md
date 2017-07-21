# hourly-notifications

Written in Python 3.5.1, for Windows.

![Screenshot](https://vgy.me/VbG6bC.png)

### Main Features
- Sets hourly alarms
- Sets alarms for a custom interval (e.g. every 42 minutes)
- Plays mp3/ogg/flac/wav files
- Can change the number of minutes into an hour alarms play at (e.g. quarter past every hour, instead of on the hour)

### How to Use
1. Install Tkinter (should come with Python3 by default), Pyglet, and AVbin.
2. After AVbin is installed, avbin.dll can be found in system32; copy and paste it into the program's folder.
3. In the program's folder, make a folder named 'sounds'. This new folder should contain sounds you want to use.
4. In the 'sounds' folder, create a folder called 'alt' and put as many sound files for the custom alarm in here as you want. When it is time for the alarm to sound, a random file will be chosen to play.

## License
Program license under [MIT](License).