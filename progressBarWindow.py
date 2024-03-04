#!/user/bin/python3
import logging
logger = logging.getLogger(__name__)
import PySimpleGUI as sg

FONT_STYLE = "any 14"
BAR_MAX = 100

gProgressWindow = None

def updateProgressWindow(theProgress):
    global gProgressWindow
    event, values = gProgressWindow.read(timeout=10)
    logger.debug(f"Updating ProgressBar Window {theProgress}")
    gProgressWindow['-PROG-'].update(theProgress + 1)
    if event == '-Interrupt-':
        return False
    return True

def openProgressWindow(message = None):
    global gProgressWindow
    if message == None:
        message = 'Progress'
    layout = [[sg.Text(message)],
            [sg.ProgressBar(BAR_MAX, orientation='h', size=(50, 20), key='-PROG-')],
            [sg.Button('Cancel',key='-Interrupt-')]]

    logger.debug("Opening ProgressBar Window")
    gProgressWindow = sg.Window('Progress', layout, font=FONT_STYLE)

def closeProgressWindow():
    global gProgressWindow
    logger.debug("Closing ProgressBar Window")
    gProgressWindow.close()

if __name__ == '__main__':
    openProgressWindow()
    for i in range(100):
        if not updateProgressWindow(i):
            break
    closeProgressWindow()