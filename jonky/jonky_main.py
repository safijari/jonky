import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject, Gdk
import cairo
import time
from tkinter import Tk, Label
from PIL import Image as PImage
from PIL import ImageTk as PImageTk
from cairo import ImageSurface, Context, FORMAT_ARGB32
import numpy as np
import cairo
from random import random
import psutil
from jonky.drawable import Color, Group


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
        array = np.ndarray(
            shape=(self.height, self.width, 4), dtype=np.uint8, buffer=buf
        )
        return array


class JonkyPS:
    def __init__(self, width, height, filename, nodes=[], background_color=None, scale=1):
        self.start_time = time.time()
        self.width = int(width * scale)
        self.height = int(height * scale)
        if ".pdf" in filename:
            self.buffer = cairo.PDFSurface(filename, self.width, self.height)
        elif ".svg" in filename:
            self.buffer = cairo.SVGSurface(filename, self.width, self.height)
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
        cr.restore()
        cr.show_page()
        self.buffer.finish()

        return self

class JonkyTk(Tk):
    def __init__(
        self, w, h, items, update_period=1, is_background=False, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.xpos, self.ypos = 0, 0
        self.drag_end = (0, 0)
        self.move_flag = False
        self.label = None
        self.items = items
        self.is_background = is_background
        self.overrideredirect(is_background)
        self.lower()
        self.geometry("{}x{}".format(w, h))
        self.update_period = update_period
        self.bind("<Button-4>", self.scroll)
        self.bind("<Button-5>", self.scroll)
        self.bind('<Button1-Motion>', self.move)
        self.bind('<ButtonRelease-1>', self.release)
        self.zoom_level = 1.0
        self.update()
        self.mainloop()

    def scroll(self, event):
        if event.num == 4:
            self.zoom_level += 0.1
        else:
            self.zoom_level -= 0.1
        self.update(queue_another=False)

    def move(self, event):
        if self.move_flag:
            sx, sy = self.drag_start
            ex, ey = self.drag_end
            new_xpos, new_ypos = event.x, event.y

            self.xpos = ex + new_xpos - sx
            self.ypos = ey + new_ypos - sy
        else:
            self.move_flag = True
            self.drag_start = (event.x, event.y)

    def release(self, event):
        self.move_flag = False
        self.drag_end = (self.xpos, self.ypos)

    def update(self, queue_another=True):
        if not self.is_background:
            w = self.winfo_width()
            h = self.winfo_height()
        else:
            w = self.winfo_screenwidth()
            h = self.winfo_screenheight()
            self.geometry("{}x{}".format(w, h))
        main_group = Group(self.items).set_pose(self.xpos, self.ypos).set_scale(self.zoom_level)
        self.ji = JonkyImage(w, h, [main_group], background_color=Color.named("black"))
        self.ji.draw()
        arr = self.ji.to_numpy()
        _image_ref = PImageTk.PhotoImage(
            PImage.fromarray(arr[:, :, :3][:, :, ::-1], "RGB")
        )
        if not self.label:
            self.label = Label(self, image=_image_ref)
            self.label.pack(expand=True, fill="both")
        else:
            # self.label.image = self._image_ref
            self.label.configure(image=_image_ref)
        self._image_ref = _image_ref
        self.arr = arr
        if queue_another:
            self.after(int(self.update_period * 1000), self.update)
