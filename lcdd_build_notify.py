#!/usr/bin/python3
import time
import datetime
import sys
import os
import signal

import pylcddc.client as client
import pylcddc.widgets as widgets
import pylcddc.screen as screen

PID_FILE_PATH = str('/tmp/lcdd_build_notify.pid')
SCREEN_TITLE = str('Build Notify')
SERVER_ADDRESS = str('localhost')
SERVER_PORT = int('13666')


class DisplayController:

    def __init__(self):
        self.start_time = None
        self.elapsed_string = None
        self.main_scr = None
        self.lcd_client = None
        self.lcd_height = None
        self.lcd_width = None

    @staticmethod
    def format_elapsed_time(c):
        return "%.2dm: %.2ds" % ((c.seconds // 60) % 60, c.seconds % 60)

    def show_screen(self):
        self.lcd_client = client.Client(SERVER_ADDRESS, SERVER_PORT)
        lcd_height = self.lcd_client.server_information_response.lcd_height
        lcd_width = self.lcd_client.server_information_response.lcd_width
        self.prepare_attributes(lcd_width, lcd_height)
        self.lcd_client.add_screen(self.main_scr)

    def update_screen(self):
        self.elapsed_string.text = "Elapsed: " + self.format_elapsed_time(datetime.datetime.now() - self.start_time)
        self.lcd_client.update_screens([self.main_scr])

    def remove_screen(self):
        self.lcd_client.delete_screen(self.main_scr)
        self.lcd_client.close()

    def prepare_attributes(self, width, height):
        title = widgets.Title('title_widget', SCREEN_TITLE)
        please_wait = widgets.Scroller('please_wait', 1, 2, width, 2,
                                       widgets.Scroller.Direction.HORIZONTAL, 8,
                                       'Please wait...')
        self.start_time = datetime.datetime.now()
        time_string = widgets.Scroller('time', 1, 3, width, 2,
                                       widgets.Scroller.Direction.HORIZONTAL, 8,
                                       'Started: ' + "{:%H:%M:%S}".format(self.start_time))
        self.elapsed_string = widgets.Scroller('elapsed', 1, 4, width, 2,
                                               widgets.Scroller.Direction.HORIZONTAL, 8, '')
        screen_configs = {
            1: [title],
            2: [title, self.elapsed_string],
            3: [title, please_wait, self.elapsed_string],
            4: [title, please_wait, time_string, self.elapsed_string]
        }

        frame_top = widgets.Frame('frame_top', screen_configs.get(height),
                                  1, 1, width, height, width, height,
                                  widgets.Frame.Direction.VERTICAL, 8)

        self.main_scr = screen.Screen('main', [frame_top],
                                      heartbeat=screen.ScreenAttributeValues.Heartbeat.OFF,
                                      priority=screen.ScreenAttributeValues.Priority.ALERT)


lcd = DisplayController()


def signal_handler(signum, frame):
    lcd.remove_screen()
    sys.exit(0)


def do_child_job():
    # Configure the child processes environment
    os.chdir("/")
    os.setsid()
    os.umask(0)
    signal.signal(signal.SIGTERM, signal_handler)

    lcd.show_screen()
    while True:
        lcd.update_screen()
        time.sleep(1)


def write_pid_to_file(pid_to_write):
    f = open(PID_FILE_PATH, 'w')
    f.write(str(pid_to_write))
    f.close()


def read_pid_from_file():
    f = open(PID_FILE_PATH, 'r')
    readed_child_pid = int(f.read())
    f.close()
    return readed_child_pid


if __name__ == "__main__":
    try:
        child_pid = read_pid_from_file()
        os.remove(PID_FILE_PATH)
        print("Killing child with pid " + str(child_pid))
        os.kill(child_pid, signal.SIGTERM)
    except FileNotFoundError:
        try:
            pid = os.fork()
            if pid > 0:
                write_pid_to_file(pid)
                # Exit parent process
                print("Exit parent process, leaving child with PID " + str(pid))
                sys.exit(0)
        except OSError as e:
            print >> sys.stderr, "fork failed: %d (%s)" % (e.errno, e.strerror)
            sys.exit(1)
        do_child_job()
