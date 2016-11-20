# hourly-notifications

### Features
- Set audio notifications to play any hour of the day, on the hour
- Play notifications as required, so long as the program is running
- Set the volume for audio
- Save choices for notifications and volume level
- Use GUI to easily choose sound files, set volume, and save settings

### Requirements
Python 3.5.1 on Windows with Tkinter, Pyglet, and AVbin. AVbin requires avbin.dll to be in the same folder as the source files. After AVbin is installed, avbin.dll can be found in system32; just copy and paste it into the hourly-notifications folder. A folder named 'sounds' must also be in the hourly-notifications folder: audio in this sound folder can be chosen as notifications.

Only .ogg files work right now, mostly because I haven't tested any other file types.

### Planned Features (in no particular order of priority)
- Support other common file types (e.g. mp3, wav)
- Allow user to choose where audio is stored
- Allow notifications to play any number of minutes into an hour (e.g. alert at 6:47, 7:47, 10:47, etc)
- Quickly set the same notification for multiple hours
