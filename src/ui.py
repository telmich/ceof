import curses
import curses.textpad

import time

stdscr = curses.initscr()

# Do not display stuff pressed
#curses.noecho()

# React on characters without return
curses.cbreak()

# Enable cursor support
stdscr.keypad(1)

begin_x = 20
begin_y = 7
height = 5
width = 40

#win = curses.newwin(height, width, begin_y, begin_x)
#stdscr.border(0)

height, width = stdscr.getmaxyx()

window = {}
window["text"] = {}
window["input"] = {}

window["input"]["height"] = 3
window["text"]["height"] = height - window["input"]["height"]
window["input"]["window"] = curses.newwin(window["input"]["height"], 0, window["text"]["height"], 0)
window["text"]["window"] = curses.newwin(window["text"]["height"], 0, 0, 0)


stdscr.addstr(10, 10, str(height) + " " + str(width) + " " + str(window["input"]["height"]) + " " + str(window["text"]["height"]))

window["input"]["window"].border(0)
window["text"]["window"].border(0)

window["input"]["window"].refresh()
window["text"]["window"].refresh()

#time.sleep(2)

#textpad = curses.textpad.Textbox(window["input"]["window"])

c = -1
window["input"]["window"].move(1,1)
while c != ord('\n'):
    c = window["input"]["window"].getch()
    window["text"]["window"].addstr(10, 10, chr(c))
    window["text"]["window"].refresh()


# Exit
curses.nocbreak()
stdscr.keypad(0)
curses.echo()
curses.endwin()
