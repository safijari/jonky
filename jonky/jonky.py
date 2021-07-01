import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk
import cairo
import time


class Jonky(object):
    """Base class for handling the window and other things

    """

    def __init__(self, period_in_sec=0.5):
        super(Jonky, self).__init__()
        self.period_in_sec = period_in_sec
        self.root = Gdk.get_default_root_window()
        self.last_run_time = None
        self.cairo_context = self.root.cairo_create()
        self.curr_time = time.time()
        self.items = []

    def run(self):
        self.draw()
        self.last_run_time = time.time()
        while True:
            self.curr_time = time.time()
            if self.curr_time - self.last_run_time >= self.period_in_sec:
                self.draw()
                self.last_run_time = self.curr_time
            time.sleep(self.period_in_sec / 10)

    def draw(self):
        cr = self.cairo_context
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        for item in self.items:
            item.draw(cr)
        self.root.process_all_updates()