import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject, Gdk
import cairo
import time

from PIL import Image as PImage
from cairo import ImageSurface, Context, FORMAT_ARGB32
import numpy as np
import cairo
from random import random
import psutil
from jonky.drawable import Color, Group, DEBUG


def switch_channel_order(inarr):
    channels = [inarr[:, :, i] for i in range(inarr.shape[-1])]
    channels = [channels[2 - i] for i in range(inarr.shape[-1])]
    return np.stack(channels, -1)


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
        self.nodes = []

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
        for item in self.nodes:
            if item.pose_transformer:
                item.pose_transformer(
                    item._pose_correction, self.curr_time - self.start_time
                )
            item.draw(cr)
        self.root.process_all_updates()
        cr.restore()


class JonkyImage:
    def __init__(self, width, height, nodes=None, background_color=None, scale=1):
        if nodes is None:
            nodes = []
        self.start_time = time.time()
        self.width = int(width * scale)
        self.height = int(height * scale)
        self.buffer = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
        self.cairo_context = cairo.Context(self.buffer)
        self.curr_time = time.time()
        self.scale = scale
        self.background_color = background_color
        self.nodes = nodes

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
        for item in self.nodes:
            if item.pose_transformer:
                item.pose_transformer(
                    item._pose_correction, self.curr_time - self.start_time
                )
            r = item.draw(cr)

            # Debug rectangle drawing
            if DEBUG:
                cr.save()
                item.pre_draw(cr)
                cr.set_source_rgb(1, 0, 1)
                cr.set_line_width(1)
                cr.rectangle(r.x, r.y, r.w, r.h)
                cr.stroke()
                item.post_draw(cr)
                cr.restore()

        cr.restore()

        return self

    def save(self, path):
        self.buffer.write_to_png(path)
        return self

    def to_numpy(self, rgb=True):
        import numpy as np

        buf = self.buffer.get_data()
        array = np.ndarray(
            shape=(self.height, self.width, 4), dtype=np.uint8, buffer=buf
        )
        if rgb:
            array = switch_channel_order(array)
        return array

    def to_opencv(self):
        return self.to_numpy(rgb=False)


class JonkyPS:
    def __init__(
        self, width, height, filename, nodes=[], background_color=None, scale=1
    ):
        self.start_time = time.time()
        self.width = int(width * scale)
        self.height = int(height * scale)
        if ".pdf" in filename:
            self.buffer = cairo.PDFSurface(filename, self.width, self.height)
        elif ".svg" in filename:
            self.buffer = cairo.SVGSurface(filename, self.width, self.height)
        self.curr_time = time.time()
        self.scale = scale
        self.background_color = background_color
        self.nodes = nodes

    def draw(self, finish=True):
        self.cairo_context = cairo.Context(self.buffer)
        cr: cairo.Context = self.cairo_context
        cr.save()
        # if self.background_color:
        #     cr.set_source_rgba(*(self.background_color.tup))
        # else:
        #     cr.set_source_rgba(0, 0, 0, 1)
        # cr.set_operator(cairo.OPERATOR_SOURCE)
        # cr.paint()
        cr.scale(self.scale, self.scale)
        rects = []
        for item in self.nodes:
            if item.pose_transformer:
                item.pose_transformer(
                    item._pose_correction, self.curr_time - self.start_time
                )
            r = item.draw(cr)
        cr.restore()
        # cr.show_page()
        self.buffer.show_page()
        if finish:
            self.buffer.finish()

        return self
