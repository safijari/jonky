import os

DEBUG = False
if os.environ.get("JONKY_DEBUG", None):
    DEBUG = True


import gi

gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")

from gi.repository import Pango as pango
from gi.repository import PangoCairo as pangocairo
from libjari.colors import color_names, convert_color_float

import math
from dataclasses import dataclass
import cairo
from PIL import Image as PImage
import PIL
from enum import Enum
import numpy as np
from threading import Thread
import time

import math

import PIL.Image as Image

color_names.update({k.replace(" ", ""): v for k, v in color_names.items()})

color_names.update(
    {
        "aliceblue": "#f0f8ff",
        "antiquewhite": "#faebd7",
        "aqua": "#00ffff",
        "aquamarine": "#7fffd4",
        "azure": "#f0ffff",
        "beige": "#f5f5dc",
        "bisque": "#ffe4c4",
        "black": "#000000",
        "blanchedalmond": "#ffebcd",
        "blue": "#0000ff",
        "blueviolet": "#8a2be2",
        "brown": "#a52a2a",
        "burlywood": "#deb887",
        "cadetblue": "#5f9ea0",
        "chartreuse": "#7fff00",
        "chocolate": "#d2691e",
        "coral": "#ff7f50",
        "cornflowerblue": "#6495ed",
        "cornsilk": "#fff8dc",
        "crimson": "#dc143c",
        "cyan": "#00ffff",
        "darkblue": "#00008b",
        "darkcyan": "#008b8b",
        "darkgoldenrod": "#b8860b",
        "darkgray": "#a9a9a9",
        "darkgrey": "#a9a9a9",
        "darkgreen": "#006400",
        "darkkhaki": "#bdb76b",
        "darkmagenta": "#8b008b",
        "darkolivegreen": "#556b2f",
        "darkorange": "#ff8c00",
        "darkorchid": "#9932cc",
        "darkred": "#8b0000",
        "darksalmon": "#e9967a",
        "darkseagreen": "#8fbc8f",
        "darkslateblue": "#483d8b",
        "darkslategray": "#2f4f4f",
        "darkslategrey": "#2f4f4f",
        "darkturquoise": "#00ced1",
        "darkviolet": "#9400d3",
        "deeppink": "#ff1493",
        "deepskyblue": "#00bfff",
        "dimgray": "#696969",
        "dimgrey": "#696969",
        "dodgerblue": "#1e90ff",
        "firebrick": "#b22222",
        "floralwhite": "#fffaf0",
        "forestgreen": "#228b22",
        "fuchsia": "#ff00ff",
        "gainsboro": "#dcdcdc",
        "ghostwhite": "#f8f8ff",
        "gold": "#ffd700",
        "goldenrod": "#daa520",
        "gray": "#808080",
        "grey": "#808080",
        "green": "#008000",
        "greenyellow": "#adff2f",
        "honeydew": "#f0fff0",
        "hotpink": "#ff69b4",
        "indianred": "#cd5c5c",
        "indigo": "#4b0082",
        "ivory": "#fffff0",
        "khaki": "#f0e68c",
        "lavender": "#e6e6fa",
        "lavenderblush": "#fff0f5",
        "lawngreen": "#7cfc00",
        "lemonchiffon": "#fffacd",
        "lightblue": "#add8e6",
        "lightcoral": "#f08080",
        "lightcyan": "#e0ffff",
        "lightgoldenrodyellow": "#fafad2",
        "lightgray": "#d3d3d3",
        "lightgrey": "#d3d3d3",
        "lightgreen": "#90ee90",
        "lightpink": "#ffb6c1",
        "lightsalmon": "#ffa07a",
        "lightseagreen": "#20b2aa",
        "lightskyblue": "#87cefa",
        "lightslategray": "#778899",
        "lightslategrey": "#778899",
        "lightsteelblue": "#b0c4de",
        "lightyellow": "#ffffe0",
        "lime": "#00ff00",
        "limegreen": "#32cd32",
        "linen": "#faf0e6",
        "magenta": "#ff00ff",
        "maroon": "#800000",
        "mediumaquamarine": "#66cdaa",
        "mediumblue": "#0000cd",
        "mediumorchid": "#ba55d3",
        "mediumpurple": "#9370db",
        "mediumseagreen": "#3cb371",
        "mediumslateblue": "#7b68ee",
        "mediumspringgreen": "#00fa9a",
        "mediumturquoise": "#48d1cc",
        "mediumvioletred": "#c71585",
        "midnightblue": "#191970",
        "mintcream": "#f5fffa",
        "mistyrose": "#ffe4e1",
        "moccasin": "#ffe4b5",
        "navajowhite": "#ffdead",
        "navy": "#000080",
        "oldlace": "#fdf5e6",
        "olive": "#808000",
        "olivedrab": "#6b8e23",
        "orange": "#ffa500",
        "orangered": "#ff4500",
        "orchid": "#da70d6",
        "palegoldenrod": "#eee8aa",
        "palegreen": "#98fb98",
        "paleturquoise": "#afeeee",
        "palevioletred": "#db7093",
        "papayawhip": "#ffefd5",
        "peachpuff": "#ffdab9",
        "peru": "#cd853f",
        "pink": "#ffc0cb",
        "plum": "#dda0dd",
        "powderblue": "#b0e0e6",
        "purple": "#800080",
        "red": "#ff0000",
        "rosybrown": "#bc8f8f",
        "royalblue": "#4169e1",
        "saddlebrown": "#8b4513",
        "salmon": "#fa8072",
        "sandybrown": "#f4a460",
        "seagreen": "#2e8b57",
        "seashell": "#fff5ee",
        "sienna": "#a0522d",
        "silver": "#c0c0c0",
        "skyblue": "#87ceeb",
        "slateblue": "#6a5acd",
        "slategray": "#708090",
        "slategrey": "#708090",
        "snow": "#fffafa",
        "springgreen": "#00ff7f",
        "steelblue": "#4682b4",
        "tan": "#d2b48c",
        "teal": "#008080",
        "thistle": "#d8bfd8",
        "tomato": "#ff6347",
        "turquoise": "#40e0d0",
        "violet": "#ee82ee",
        "wheat": "#f5deb3",
        "white": "#ffffff",
        "whitesmoke": "#f5f5f5",
        "yellow": "#ffff00",
        "yellowgreen": "#9acd32",
    }
)


def _rad(deg):
    return deg * math.pi / 180


def _ccf(color):
    if color is None:
        return color
    return convert_color_float(color.lower().replace(" ", ""))


def from_pil(im, alpha=1.0, format=cairo.FORMAT_ARGB32):
    """
    :param im: Pillow Image
    :param alpha: 0..1 alpha to add to non-alpha images
    :param format: Pixel format for output surface
    """
    assert format in (cairo.FORMAT_RGB24, cairo.FORMAT_ARGB32), (
        "Unsupported pixel format: %s" % format
    )
    if "A" not in im.getbands():
        im.putalpha(int(alpha * 256.0))
    arr = bytearray(im.tobytes("raw", "BGRa"))
    surface = cairo.ImageSurface.create_for_data(arr, format, im.width, im.height)
    return surface


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
    """yaw is in deg"""

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
        if isinstance(r, Color):
            r, g, b = r.r, r.g, r.b
        if isinstance(r, str):
            r, g, b = _ccf(r)
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
    """Documentation for Drawable"""

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
        self.packing_corrections = Point2(0, 0)

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

    def pre_draw(self, ctx, do_xform=True, dpi_converter=None):
        ctx.save()
        ctx.set_source_rgba(*(self.color.tup))
        if self.color.a != 1.0 or (self.fill_color and self.fill_color.a != 1.0):
            ctx.set_operator(cairo.OPERATOR_ATOP)
        if do_xform:
            if not dpi_converter:
                ctx.translate(self.pose.x, self.pose.y)
            else:
                ctx.translate(*dpi_converter(self.pose.x, self.pose.y))
            if self.scale:
                ctx.scale(self.scale, self.scale)
            ctx.rotate(self.pose.yaw_rad)

    def post_draw(self, ctx):
        ctx.restore()

    def draw(self, ctx, dpi_converter=None):
        pass


class Group(Drawable):
    def __init__(self, nodes=None, packing=None, pack_padding=0, *args, **kwargs):
        super(Group, self).__init__(*args, **kwargs)
        self.packing = packing
        if isinstance(self.packing, str):
            self.packing = Packing(self.packing)
        self.pack_padding = pack_padding
        if packing is None:
            self.packing = Packing.NONE
        assert self.packing != Packing.GRID
        self.nodes = nodes if nodes is not None else []

    def draw(self, ctx, do_xform=True, dpi_converter=None):
        # print(f"drawing {type(self)}")
        self.pre_draw(ctx, do_xform)
        rect = None
        xshift = 0
        yshift = 0
        for i, node in enumerate(self.nodes):
            if self.packing != Packing.NONE:
                if self.packing == Packing.VERTICAL:
                    node.set_pose(
                        node.packing_corrections.x, yshift + node.packing_corrections.y
                    )
                if self.packing == Packing.HORIZONTAL:
                    node.set_pose(
                        xshift + node.packing_corrections.x, node.packing_corrections.y
                    )
            _rect = node.draw(ctx, dpi_converter=dpi_converter)
            if self.packing == Packing.NONE:
                _rect.x += node.pose.x
                _rect.y += node.pose.y

            if rect is None:
                rect = _rect
            else:
                _rect.x += xshift + node.packing_corrections.x
                _rect.y += yshift + node.packing_corrections.y
                rect = rect + _rect

            # Debug rectangle drawing
            if DEBUG:
                r = _rect
                ctx.set_source_rgb(0, 0, 1)
                ctx.set_line_width(2)
                ctx.rectangle(r.x, r.y, r.w, r.h)
                ctx.stroke()

            if self.packing != Packing.NONE:
                if self.packing == Packing.VERTICAL:
                    if dpi_converter:
                        yshift += _rect.h + dpi_converter(self.pack_padding)
                    else:
                        yshift += _rect.h + self.pack_padding
                if self.packing == Packing.HORIZONTAL:
                    if dpi_converter:
                        xshift += _rect.w + dpi_converter(self.pack_padding)
                    else:
                        xshift += _rect.w + self.pack_padding
        self.post_draw(ctx)
        return rect.scale(self.scale)


class BakedGroup(Group):
    def __init__(self, *args, **kwargs):
        super(BakedGroup, self).__init__(*args, **kwargs)
        self.surface = None

    def draw(self, ctx: cairo.Context, dpi_converter=None):
        if not self.surface:
            size = super(BakedGroup, self).draw(ctx, True, dpi_converter=dpi_converter)
            self.surface = cairo.ImageSurface(
                cairo.FORMAT_ARGB32, int(size.w) * 2, int(size.h) * 2
            )
            surface_ctx = cairo.Context(self.surface)
            surface_ctx.scale(2.0, 2.0)

            surface_ctx.set_source_rgba(1.0, 1.0, 1.0, 0.0)
            surface_ctx.set_operator(cairo.OPERATOR_SOURCE)
            surface_ctx.paint()

            super(BakedGroup, self).draw(surface_ctx, False, dpi_converter=dpi_converter)
            self.surface.write_to_png("/tmp/test.png")
        else:
            self.pre_draw(ctx, True, dpi_converter=dpi_converter)
            ctx.scale(0.5, 0.5)
            ctx.rectangle(0, 0, self.surface.get_width(), self.surface.get_height())
            ctx.set_source_rgba(0, 0, 0, 0.0)
            ctx.set_source_surface(self.surface)
            ctx.clip()
            ctx.set_operator(cairo.OPERATOR_ATOP)
            ctx.paint()
            self.post_draw(ctx)


class Text(Drawable):
    """Documentation for Text"""

    def __init__(self, font, font_size, text, on_bottom=False, *args, **kwargs):
        super(Text, self).__init__(*args, **kwargs)
        self.font = font
        self.font_size = font_size
        self.text = text
        self.on_bottom = on_bottom

    def draw(self, ctx, dpi_converter=None):
        super(Text, self).draw(ctx, dpi_converter=dpi_converter)
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

            self.pre_draw(ctx, dpi_converter=dpi_converter)
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
    """Documentation for Text"""

    def __init__(
        self,
        text,
        font_size=50,
        font="Arial",
        alignment="left",
        width=None,
        line_spacing=1,
        *args,
        **kwargs,
    ):
        super(PangoText, self).__init__(*args, **kwargs)
        self.font = font
        self.font_size = font_size
        self.text = text
        self.width = width if width else 10000
        self.alignment = alignment
        self.line_spacing = line_spacing

    def draw(self, ctx, dpi_converter=None):
        super(PangoText, self).draw(ctx, dpi_converter=dpi_converter)
        self.pre_draw(ctx, dpi_converter=dpi_converter)

        layout = pangocairo.create_layout(ctx)
        if not dpi_converter:
            layout.set_width(pango.units_from_double(self.width))
            layout.set_line_spacing(self.line_spacing)
            layout.set_font_description(
                pango.FontDescription(f"{self.font} {self.font_size}")
            )
        else:
            layout.set_width(pango.units_from_double(dpi_converter(self.width)))
            layout.set_line_spacing(dpi_converter(self.line_spacing))
            layout.set_font_description(
                pango.FontDescription(
                    f"{self.font} {dpi_converter(self.font_size)}"
                )
            )
        alignment = pango.Alignment.LEFT
        if self.alignment == "right":
            alignment = pango.Alignment.RIGHT
        if self.alignment == "center":
            alignment = pango.Alignment.CENTER
        layout.set_alignment(alignment)
        layout.set_markup(self.text)

        pangocairo.show_layout(ctx, layout)

        r = layout.get_pixel_extents()[0]

        self.post_draw(ctx)
        return Rect(r.x, r.y, r.width, r.height)


class JImage(Drawable):
    def __init__(self, src, opacity=1.0, *args, **kwargs):
        super(JImage, self).__init__(*args, **kwargs)
        self.src = None
        if isinstance(src, np.ndarray):
            if len(src.shape) == 2:
                _im = PImage.fromarray(src, "L")
                _im = _im.convert(mode="RGB")
                self.src = from_pil(_im, alpha=opacity)
            elif len(src.shape) == 3 and src.shape[2] == 3:
                self.src = from_pil(PImage.fromarray(src, "RGB"), alpha=opacity)
            elif len(src.shape) == 3 and src.shape[2] == 4:
                self.src = from_pil(PImage.fromarray(src, "RGBA"), alpha=opacity)
            else:
                raise Exception("uhhhh")
            return
        if isinstance(src, str):
            self.src = from_pil(PImage.open(src), alpha=opacity)

        # apparently there's no good way to figure out if an image is a PIL image ...
        if self.src is None:
            self.src = from_pil(src, alpha=opacity)

    def draw(self, ctx: cairo.Context, dpi_converter=None):
        super(JImage, self).draw(ctx, dpi_converter=dpi_converter)
        self.pre_draw(ctx, dpi_converter=dpi_converter)
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

    def draw(self, ctx: cairo.Context, dpi_converter=None):
        pass


class Arc(Shape):
    def __init__(self, radius, start_angle, end_angle, *args, **kwargs):
        super(Arc, self).__init__(*args, **kwargs)
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.radius = radius

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, val):
        self._radius = val
        self.packing_corrections.x = val
        self.packing_corrections.y = val

    def draw(self, ctx: cairo.Context, dpi_converter=None):
        self.pre_draw(ctx, dpi_converter=dpi_converter)
        ctx.set_line_width(self.stroke_width)
        ctx.arc(
            0,
            0,
            self.radius,
            self.start_angle * math.pi / 180,
            self.end_angle * math.pi / 180,
        )
        r = Rect.from_extents(ctx.stroke_extents())
        # if not self.center_based:
        #     r.x += self.radius
        #     r.y += self.radius
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

    def draw(self, ctx: cairo.Context, dpi_converter=None):
        self.pre_draw(ctx, dpi_converter=dpi_converter)
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

    def draw(self, ctx: cairo.Context, dpi_converter=None):
        self.pre_draw(ctx, dpi_converter=dpi_converter)
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
        self,
        start_angle,
        end_angle,
        start_radius,
        end_radius,
        ccw=False,
        *args,
        **kwargs,
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
                    curr_r * math.cos(step * angle * math.pi / 180),
                    curr_r * math.sin(step * angle * math.pi / 180),
                )
            )
            curr_r += exp

        self.point_list = pts

RichText = PangoText