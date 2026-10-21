
import sys
import curses

from grass import VERSION
from grass.editor import run

USAGE = "usage: grass [file]\n       grass --version"


def reset_cursor():
    try:
        sys.stdout.write("\x1b[0 q")
        sys.stdout.flush()
    except OSError:
        pass


def main():
    args = sys.argv[1:]
    if len(args) >= 1 and (args[0] == "--version" or args[0] == "-v"):
        print("grass " + VERSION + " · Meadow")
        return
    if len(args) >= 1 and (args[0] == "--help" or args[0] == "-h"):
        print(USAGE)
        return
    path = None
    if len(args) >= 1:
        path = args[0]
    try:
        curses.wrapper(run, path)
    except KeyboardInterrupt:
        pass
    reset_cursor()
