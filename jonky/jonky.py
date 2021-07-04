import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject, Gdk
import cairo
import time
from jonky.drawable import Color

class Jonky(object):
    """Base class for handling the window and other things

    """

    def __init__(self, period_in_sec=0.5, target_size=None):
        super(Jonky, self).__init__()
        self.start_time = time.time()
        self.period_in_sec = period_in_sec
        self.root = Gdk.get_default_root_window()
        self.last_run_time = None
        rww = self.root.get_width()
        rwh = self.root.get_height()
        self.buffer = cairo.ImageSurface(cairo.FORMAT_ARGB32, rww, rwh)
        self.cairo_context = cairo.Context(self.buffer)
        self.cairo_context_root = self.root.cairo_create()
        self.curr_time = time.time()
        self.target_size = target_size
        self.items = []

    def run(self):
        self.draw()
        self.last_run_time = time.time()
        while True:
            self.curr_time = time.time()
            if self.curr_time - self.last_run_time >= self.period_in_sec:
                self.draw()
                self.last_run_time = self.curr_time
            self.draw_buffer()
            time.sleep(1 / 10)

    def draw_buffer(self):
        crr = self.cairo_context_root
        crr.save()
        # crr.set_source_rgb(1.0, 1.0, 1.0)
        crr.set_operator(cairo.OPERATOR_SOURCE)
        # crr.paint()
        crr.set_source_surface(self.buffer)
        crr.paint()
        crr.restore()

    def draw(self):
        if self.target_size:
            rww = self.root.get_width()
            rwh = self.root.get_height()
            sx = rww / self.target_size[0]
            sy = rwh / self.target_size[1]

        cr: cairo.Context = self.cairo_context
        cr.save()
        if self.target_size:
            cr.scale(sx, sy)
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        for item in self.items:
            if item.pose_transformer:
                item.pose_transformer(
                    item._pose_correction, self.curr_time - self.start_time
                )
            item.draw(cr)
        self.root.process_all_updates()
        cr.restore()


class JonkyImage:
    def __init__(self, width, height, nodes, background_color="black", scale=1):
        self.start_time = time.time()
        self.buffer = cairo.ImageSurface(cairo.FORMAT_ARGB32, width*scale, height*scale)
        self.cairo_context = cairo.Context(self.buffer)
        self.curr_time = time.time()
        self.scale = scale
        self.background_color = Color.new(background_color)
        self.items = nodes

    def draw(self):
        cr: cairo.Context = self.cairo_context
        cr.save()
        cr.set_source_rgba(*(self.background_color.tup))
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.scale(self.scale, self.scale)
        for item in self.items:
            if item.pose_transformer:
                item.pose_transformer(
                    item._pose_correction, self.curr_time - self.start_time
                )
            item.draw(cr)
        cr.restore()
        return self

    def save(self, path):
        self.buffer.write_to_png(path)
        return self
