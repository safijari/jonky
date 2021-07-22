import gi

gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")

from gi.repository import Pango as pango
from gi.repository import PangoCairo as pangocairo

from libjari.colors import convert_color_float
import math
from dataclasses import dataclass
import cairo
from jonky.helpers import from_pil, _rad
from PIL import Image as PImage
import PIL
from enum import Enum
import numpy as np
from threading import Thread
import time


def _ccf(color):
    if color is None:
        return color
    return convert_color_float(color)


def updater_wrapper(fn, self, attr_name, period):
    start_time = time.time()
    while True:
        curr_time = time.time()
        if curr_time - start_time >= period:
            out = fn(self)
            if attr_name:
                self.__setattr__(attr_name, out)
            start_time = curr_time
        else:
            time.sleep(period / 10)


class Pose:
    """yaw is in deg

    """

    def __init__(self, x=0, y=0, yaw=0):
        self.x = x
        self.y = y
        self.yaw = yaw

    @property
    def yaw_rad(self):
        return self.yaw * math.pi / 180

    @property
    def do_translate(self):
        return self.x != 0 or self.y != 0

    @property
    def do_rotate(self):
        return self.yaw != 0

    def __add__(self, b):
        a = self
        return Pose(a.x + b.x, a.y + b.y, a.yaw + b.yaw)


class Color:
    def __init__(self, r=0, g=0, b=0, a=1):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        if any([r > 1, g > 1, b > 1, a > 1]):
            self.r = r / 255
            self.g = g / 255
            self.b = b / 255
            self.a = a / 255

    @classmethod
    def named(cls, name, alpha=1.0):
        return cls(*(_ccf(name)), alpha)

    @property
    def tup(self):
        return (self.r, self.g, self.b, self.a)

    @classmethod
    def new(cls, inp):
        if inp is None:
            return cls()
        if isinstance(inp, cls):
            return inp
        if isinstance(inp, str):
            return Color.named(inp)
        if isinstance(inp, tuple):
            assert len(inp) in [3, 4], "color invalid"
            if len(inp) == 3:
                return cls(*inp, 1.0)
            return cls(*inp)


@dataclass
class Rect:
    x: float
    y: float
    w: float
    h: float

    @property
    def y2(self):
        return self.y + self.h

    @property
    def x2(self):
        return self.x + self.w

    @classmethod
    def from_extents(cls, extents):
        x1, y1, x2, y2 = extents
        return cls(x1, y1, x2 - x1, y2 - y1)

    def __add__(self, other):
        x = min(self.x, other.x)
        y = min(self.y, other.y)
        w = max(self.x + self.w, other.x + other.w) - x
        h = max(self.y + self.h, other.y + other.h) - y
        return Rect(x, y, w, h)

    def scale(self, scale):
        return Rect(self.x * scale, self.y * scale, self.w * scale, self.h * scale)


@dataclass
class Point2:
    x: float
    y: float

    @classmethod
    def from_tup(cls, tup):
        return cls(*tup)

    @classmethod
    def new(cls, inp):
        if isinstance(inp, Point2):
            return inp
        if isinstance(inp, tuple):
            return cls.from_tup(inp)

        raise Exception("can't make point2")

    @property
    def tup(self):
        return (self.x, self.y)


class Packing(Enum):
    NONE = "none"
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    GRID = "grid"


class Drawable:
    """Documentation for Drawable

    """

    def __init__(
        self, pose=None, color=None, scale=1.0, fill_color=None, pose_transformer=None
    ):
        self.color = Color.new(color)
        self.fill_color = Color.new(fill_color) if fill_color else None
        if pose is None:
            pose = Pose()
        self._pose = pose
        self._pose_correction = Pose()
        self.pose_transformer = None
        self.scale = scale
        self.thread = None

    @property
    def pose(self):
        return self._pose + self._pose_correction

    @pose.setter
    def pose(self, val):
        self._pose = val

    def set_pose(self, x=None, y=None, yaw=None):
        p = self.pose
        if x:
            p.x = x
        if y:
            p.y = y
        if yaw:
            p.yaw = yaw
        self.pose = p
        return self

    def set_scale(self, scale):
        self.scale = scale
        return self

    def set_updater(self, fn, attr_name, period):
        self.thread = Thread(target=updater_wrapper, args=(fn, self, attr_name, period))
        self.thread.daemon = True
        self.thread.start()
        return self

    def set_pose_transformer(self, transformer):
        self.pose_transformer = transformer
        return self

    def set_alpha(self, alpha):
        self.color.a = alpha
        return self

    def pre_draw(self, ctx, do_xform=True):
        ctx.save()
        ctx.set_source_rgba(*(self.color.tup))
        if self.color.a != 1.0 or (self.fill_color and self.fill_color.a != 1.0):
            ctx.set_operator(cairo.OPERATOR_ATOP)
        if do_xform:
            ctx.translate(self.pose.x, self.pose.y)
            if self.scale:
                ctx.scale(self.scale, self.scale)
            ctx.rotate(self.pose.yaw_rad)

    def post_draw(self, ctx):
        ctx.restore()

    def draw(self, ctx):
        pass


class Group(Drawable):
    def __init__(self, nodes=None, packing=None, pack_padding=0, *args, **kwargs):
        super(Group, self).__init__(*args, **kwargs)
        self.packing = packing
        self.pack_padding = pack_padding
        if packing is None:
            self.packing = Packing.NONE
        assert self.packing != Packing.GRID
        self.nodes = nodes if nodes is not None else []

    def draw(self, ctx, do_xform=True):
        # print(f"drawing {type(self)}")
        self.pre_draw(ctx, do_xform)
        rect = None
        xshift = 0
        yshift = 0
        for i, node in enumerate(self.nodes):
            if self.packing != Packing.NONE:
                if self.packing == Packing.VERTICAL:
                    node.set_pose(0, yshift)
                if self.packing == Packing.HORIZONTAL:
                    node.set_pose(xshift, 0)
            _rect = node.draw(ctx)
            if self.packing == Packing.NONE:
                _rect.x += node.pose.x
                _rect.y += node.pose.y
            # Debug rectangle drawing
            # r = _rect
            # ctx.set_source_rgb(0, 0, 1)
            # ctx.set_line_width(2)
            # ctx.rectangle(r.x, r.y, r.w, r.h)
            # ctx.stroke()
            if rect is None:
                rect = _rect
            else:
                _rect.x += xshift
                _rect.y += yshift
                rect = rect + _rect
            if self.packing != Packing.NONE:
                if self.packing == Packing.VERTICAL:
                    yshift += _rect.h + self.pack_padding
                if self.packing == Packing.HORIZONTAL:
                    xshift += _rect.w + self.pack_padding
        self.post_draw(ctx)
        return rect.scale(self.scale)


class BakedGroup(Group):
    def __init__(self, *args, **kwargs):
        super(BakedGroup, self).__init__(*args, **kwargs)
        self.surface = None

    def draw(self, ctx: cairo.Context):
        if not self.surface:
            size = super(BakedGroup, self).draw(ctx, True)
            self.surface = cairo.ImageSurface(
                cairo.FORMAT_ARGB32, int(size.w) * 2, int(size.h) * 2
            )
            surface_ctx = cairo.Context(self.surface)
            surface_ctx.scale(2.0, 2.0)

            surface_ctx.set_source_rgba(1.0, 1.0, 1.0, 0.0)
            surface_ctx.set_operator(cairo.OPERATOR_SOURCE)
            surface_ctx.paint()

            super(BakedGroup, self).draw(surface_ctx, False)
            self.surface.write_to_png("/tmp/test.png")
        else:
            self.pre_draw(ctx, True)
            ctx.scale(0.5, 0.5)
            ctx.rectangle(0, 0, self.surface.get_width(), self.surface.get_height())
            ctx.set_source_rgba(0, 0, 0, 0.0)
            ctx.set_source_surface(self.surface)
            ctx.clip()
            ctx.set_operator(cairo.OPERATOR_ATOP)
            ctx.paint()
            self.post_draw(ctx)


class Text(Drawable):
    """Documentation for Text

    """

    def __init__(self, font, font_size, text, on_bottom=False, *args, **kwargs):
        super(Text, self).__init__(*args, **kwargs)
        self.font = font
        self.font_size = font_size
        self.text = text
        self.on_bottom = on_bottom

    def draw(self, ctx):
        super(Text, self).draw(ctx)
        yshift = 0
        x, y = self.pose.x, self.pose.y
        w = 0
        h = 0
        rect = None
        for line in self.text.split("\n"):
            ctx.select_font_face(self.font)
            ctx.set_font_size(self.font_size)
            (x, y, width, height, dx, dy) = ctx.text_extents(self.text)
            w = max(width, w)

            self.pre_draw(ctx)
            ctx.translate(0, yshift)
            if not self.on_bottom:
                ctx.translate(-x, -y)

            ctx.show_text(line)
            if rect is None:
                rect = Rect(-x, -y, width, height)
            else:
                rect += Rect(-x, -y - yshift, width, height)
            ctx.stroke()
            yshift += self.font_size
            self.post_draw(ctx)
        h = yshift
        return rect


class PangoText(Drawable):
    """Documentation for Text

    """

    def __init__(
        self, font, font_size, text, alignment="left", width=None, *args, **kwargs
    ):
        super(PangoText, self).__init__(*args, **kwargs)
        self.font = font
        self.font_size = font_size
        self.text = text
        self.width = width if width else 10000
        self.alignment = alignment

    def draw(self, ctx):
        super(PangoText, self).draw(ctx)
        self.pre_draw(ctx)

        layout = pangocairo.create_layout(ctx)
        layout.set_width(pango.units_from_double(self.width))
        alignment = pango.Alignment.LEFT
        if self.alignment == "right":
            alignment = pango.Alignment.RIGHT
        if self.alignment == "center":
            alignment = pango.Alignment.CENTER
        layout.set_alignment(alignment)
        layout.set_font_description(
            pango.FontDescription(f"{self.font} {self.font_size}")
        )
        layout.set_markup(self.text)

        pangocairo.show_layout(ctx, layout)

        r = layout.get_pixel_extents()[0]

        self.post_draw(ctx)
        return Rect(r.x, r.y, r.width, r.height)


class Image(Drawable):
    def __init__(self, src, opacity=1.0, *args, **kwargs):
        super(Image, self).__init__(*args, **kwargs)
        self.src = None
        if isinstance(src, np.ndarray):
            if len(src.shape) == 3:
                self.src = from_pil(PImage.fromarray(src, "RGB"), alpha=opacity)
            elif len(src.shape) == 4:
                self.src = from_pil(PImage.fromarray(src, "RGBA"), alpha=opacity)
            else:
                raise Exception("uhhhh")
            return
        if isinstance(src, str):
            self.src = from_pil(PImage.open(src), alpha=opacity)

        # apparently there's no good way to figure out if an image is a PIL image ...
        if self.src is None:
            self.src = from_pil(src, alpha=opacity)

    def draw(self, ctx: cairo.Context):
        super(Image, self).draw(ctx)
        self.pre_draw(ctx)
        ctx.set_source_rgba(0, 0, 0, 0.0)

        # ctx.translate(-self.src.get_width() / 2, -self.src.get_height() / 2)

        ctx.rectangle(0, 0, self.src.get_width(), self.src.get_height())
        ctx.set_operator(cairo.OPERATOR_OVER)
        ctx.set_source_surface(self.src)
        ctx.clip()
        ctx.paint()

        self.post_draw(ctx)
        out_rect = Rect(0, 0, self.src.get_width(), self.src.get_height())
        return out_rect.scale(self.scale)


class Shape(Drawable):
    def __init__(self, stroke_width=1, *args, **kwargs):
        super(Shape, self).__init__(*args, **kwargs)
        # assert fill_color is None
        self.stroke_width = stroke_width

    def draw(self, ctx: cairo.Context):
        pass


class Arc(Shape):
    def __init__(self, radius, start_angle, end_angle, *args, **kwargs):
        super(Arc, self).__init__(*args, **kwargs)
        self.radius = radius
        self.start_angle = start_angle
        self.end_angle = end_angle

    def draw(self, ctx: cairo.Context):
        self.pre_draw(ctx)
        ctx.set_line_width(self.stroke_width)
        ctx.arc(
            0,
            0,
            self.radius,
            self.start_angle * math.pi / 180,
            self.end_angle * math.pi / 180,
        )
        r = Rect.from_extents(ctx.stroke_extents())
        if self.fill_color:
            ctx.set_source_rgba(*(self.fill_color.tup))
            ctx.fill_preserve()
            ctx.set_source_rgba(*(self.color.tup))
            ctx.stroke()
        else:
            ctx.stroke()
        self.post_draw(ctx)
        return r


class Circle(Arc):
    def __init__(self, radius, *args, **kwargs):
        super(Circle, self).__init__(radius, 0, 360, *args, **kwargs)


class Polygon(Shape):
    def __init__(self, point_list, *args, **kwargs):
        super(Polygon, self).__init__(*args, **kwargs)
        self.point_list = [Point2.new(p) for p in point_list]

    def draw(self, ctx: cairo.Context):
        self.pre_draw(ctx)
        ctx.set_line_width(self.stroke_width)
        ctx.move_to(*(self.point_list[0].tup))
        for pt in self.point_list[1:]:
            ctx.line_to(*(pt.tup))

        rect = Rect.from_extents(ctx.stroke_extents())
        if self.fill_color:
            ctx.set_source_rgba(*(self.fill_color.tup))
            ctx.fill_preserve()
            ctx.set_source_rgba(*(self.color.tup))
            ctx.stroke()
        else:
            ctx.stroke()
        self.post_draw(ctx)
        return rect


class Rectangle(Shape):
    def __init__(self, width, height, corner_radius=0, *args, **kwargs):
        super(Rectangle, self).__init__(*args, **kwargs)
        self.width = width
        self.height = height
        self.corner_radius = corner_radius

    def draw(self, ctx: cairo.Context):
        self.pre_draw(ctx)
        w, h, r = self.width, self.height, self.corner_radius
        r = min(r, w / 2, h / 2)
        ctx.set_line_width(self.stroke_width)
        ctx.move_to(r, 0)
        ctx.line_to(w - r, 0)
        if r != 0:
            ctx.arc(w - r, r, r, _rad(-90), 0)
        ctx.line_to(w, h - r)

        if r != 0:
            ctx.arc(w - r, h - r, r, _rad(0), _rad(90))

        ctx.line_to(r, h)

        if r != 0:
            ctx.arc(r, h - r, r, _rad(90), _rad(180))

        ctx.line_to(0, r)

        if r != 0:
            ctx.arc(r, r, r, _rad(180), _rad(270))

        rect = Rect.from_extents(ctx.stroke_extents())
        if self.fill_color:
            ctx.set_source_rgba(*(self.fill_color.tup))
            ctx.fill_preserve()
            ctx.set_source_rgba(*(self.color.tup))
            ctx.stroke()
        else:
            ctx.stroke()
        self.post_draw(ctx)

        return rect.scale(self.scale)


class Spiral(Polygon):
    def __init__(
            self, start_angle, end_angle, start_radius, end_radius, ccw=False, *args, **kwargs
    ):
        super().__init__([], *args, **kwargs)
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.start_radius = start_radius
        self.end_radius = end_radius
        self.ccw = ccw
        self.compute_points()

    def compute_points(self):
        pts = []
        curr_r = self.start_radius
        exp = (self.end_radius - self.start_radius) / (
            self.end_angle - self.start_angle
        )
        step = -1 if self.ccw else 1
        for angle in range(self.start_angle, self.end_angle):
            pts.append(
                Point2(
                    curr_r * math.cos(step*angle * math.pi / 180),
                    curr_r * math.sin(step*angle * math.pi / 180),
                )
            )
            curr_r += exp

        self.point_list = pts
