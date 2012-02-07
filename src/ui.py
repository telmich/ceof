import curses
import time

stdscr = curses.initscr()

# Do not display stuff pressed
curses.noecho()

# React on characters without return
curses.cbreak()

# Enable cursor support
stdscr.keypad(1)

begin_x = 20
begin_y = 7
height = 5
width = 40

#win = curses.newwin(height, width, begin_y, begin_x)
stdscr.border(0)
stdscr.refresh()

time.sleep(2)


# Exit
curses.nocbreak()
stdscr.keypad(0)
curses.echo()
