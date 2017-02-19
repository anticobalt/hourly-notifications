# Converts preference file from an older format to the format compatible with current code

from filehandling import System

CURRENT_PROGRAM_VERSION = "Conundrum"

if System.convert_preferences():
    print("Success.")
else:
    print("Failure.")

x = input()
