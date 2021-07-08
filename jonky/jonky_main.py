import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject, Gdk
import cairo
import time
# from jonky.jonky.drawable import Color


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
    def __init__(self, width, height, nodes, background_color=None, scale=1):
        self.start_time = time.time()
        self.width = int(width * scale)
        self.height = int(height * scale)
        self.buffer = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        self.cairo_context = cairo.Context(self.buffer)
        self.curr_time = time.time()
        self.scale = scale
        self.background_color = background_color
        self.items = nodes

    def draw(self):
        cr: cairo.Context = self.cairo_context
        cr.save()
        if self.background_color:
            cr.set_source_rgba(*(self.background_color.tup))
        else:
            cr.set_source_rgba(0, 0, 0, 1)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.scale(self.scale, self.scale)
        rects = []
        for item in self.items:
            if item.pose_transformer:
                item.pose_transformer(
                    item._pose_correction, self.curr_time - self.start_time
                )
            r = item.draw(cr)
            # debug rectangle drawing
            # cr.save()
            # item.pre_draw(cr)
            # cr.set_source_rgb(1, 0, 1)
            # cr.set_line_width(1)
            # cr.rectangle(r.x, r.y, r.w, r.h)
            # cr.stroke()
            # item.post_draw(cr)
            # cr.restore()
        cr.restore()

        return self

    def save(self, path):
        self.buffer.write_to_png(path)
        return self

    def to_numpy(self):
        import numpy as np
        buf = self.buffer.get_data()
        array = np.ndarray(shape=(self.height, self.width, 4), dtype=np.uint8, buffer=buf)
        return array


class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Hello World")
        self.set_keep_above(False)
        self.set_keep_below(True)
        self.set_type_hint(Gdk.WindowTypeHint.DESKTOP)
        self.set_decorated(False)
        self.set_accept_focus(False)
        self.stick()
        self.connect("destroy", Gtk.main_quit)
        darea = Gtk.DrawingArea()
        darea.connect("draw", self.draw)
        self.add(darea)
        self.i = 0
        # self.button = Gtk.Button(label="Click Here")
        # self.button.connect("clicked", self.on_button_clicked)
        # self.add(self.button)

    def draw(self, event, cr):

        import math
        cr.set_line_width(9)
        cr.set_source_rgb(0.7, 0.2, 0.0)
                
        win = self.get_window()
        w = win.get_width()
        h = win.get_height()

        cr.translate(w/2, h/2)
        cr.arc(0, 0, 50, 0, 2*math.pi)
        cr.stroke_preserve()
        
        cr.set_source_rgb(0.3, 0.4, 0.6)
        cr.fill()
        print("Hello World", self.i)
        self.i += 1
