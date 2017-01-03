from HourlyNotifications_FileHandling import System

CURRENT_PROGRAM_VERSION = "Bauxite"

if System.convert_preferences():
    print("Success.")
else:
    print("Failure.")

x = input()
