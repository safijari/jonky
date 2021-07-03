from libjari.colors import convert_color_float
import math
from dataclasses import dataclass
import cairo
from jonky.helpers import from_pil
from PIL import Image as PImage
import PIL
from enum import Enum


def _ccf(color):
    if color is None:
        return color
    return convert_color_float(color)


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
            assert len(tuple) in [3, 4], "color invalid"
            if len(inp) == 3:
                return cls(*inp, 1.0)
            return cls(*inp)


@dataclass
class Rect:
    x: float
    y: float
    w: float
    h: float


class Packing(Enum):
    NONE = "none"
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    GRID = "grid"


class Drawable:
    """Documentation for Drawable

    """

    def __init__(self, pose=None, color=None, pose_transformer=None):
        self.color = Color.new(color)
        if pose is None:
            pose = Pose()
        self._pose = pose
        self._pose_correction = Pose()
        self.pose_transformer = None

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

    def set_pose_transformer(self, transformer):
        self.pose_transformer = transformer
        return self

    def pre_draw(self, ctx, do_xform=True):
        ctx.save()
        ctx.set_source_rgba(*(self.color.tup))
        if do_xform:
            ctx.translate(self.pose.x, self.pose.y)
            ctx.rotate(self.pose.yaw_rad)

    def post_draw(self, ctx):
        ctx.restore()

    def draw(self, ctx):
        pass


class Group(Drawable):
    def __init__(self, nodes, packing=None, pack_padding=0, *args, **kwargs):
        super(Group, self).__init__(*args, **kwargs)
        self.packing = packing
        self.pack_padding = pack_padding
        if packing is None:
            self.packing = Packing.NONE
        assert self.packing != Packing.GRID
        self.nodes = nodes

    def draw(self, ctx, do_xform=True):
        self.pre_draw(ctx, do_xform)
        rect = Rect(self.pose.x, self.pose.y, 0, 0)
        for i, node in enumerate(self.nodes):
            if self.packing != Packing.NONE:
                if self.packing == Packing.VERTICAL:
                    node.set_pose(0, rect.h + i * self.pack_padding)
                if self.packing == Packing.HORIZONTAL:
                    node.set_pose(rect.w + i * self.pack_padding, 0)
            _rect = node.draw(ctx)
            if self.packing != Packing.NONE:
                if self.packing == Packing.VERTICAL:
                    rect.h += _rect.h + self.pack_padding
                    rect.w = max(rect.w, _rect.w)
                if self.packing == Packing.HORIZONTAL:
                    rect.w += _rect.w + self.pack_padding
                    rect.h = max(rect.h, _rect.h)
        self.post_draw(ctx)
        return rect


class BakedGroup(Group):
    def __init__(self, *args, **kwargs):
        super(BakedGroup, self).__init__(*args, **kwargs)
        self.surface = None

    def draw(self, ctx: cairo.Context):
        if not self.surface:
            size = super(BakedGroup, self).draw(ctx, True)
            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(size.w + 1)*2, int(size.h + 1)*2)
            surface_ctx = cairo.Context(self.surface)
            surface_ctx.scale(2.0, 2.0)

            surface_ctx.set_source_rgba(1.0, 1.0, 1.0, 0.0)
            surface_ctx.set_operator(cairo.OPERATOR_SOURCE)
            surface_ctx.paint()

            super(BakedGroup, self).draw(surface_ctx, False)
            # self.surface.write_to_png("/tmp/test.png")
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

    def __init__(self, font, font_size, text, *args, **kwargs):
        super(Text, self).__init__(*args, **kwargs)
        self.font = font
        self.font_size = font_size
        self.text = text

    def draw(self, ctx):
        super(Text, self).draw(ctx)
        yshift = 0
        x, y = self.pose.x, self.pose.y
        w = 0
        h = 0
        for line in self.text.split("\n"):
            ctx.select_font_face(self.font)
            ctx.set_font_size(self.font_size)
            (x, y, width, height, dx, dy) = ctx.text_extents(self.text)
            w = max(width, w)

            self.pre_draw(ctx)
            ctx.translate(0, yshift)
            ctx.translate(-x, -y)

            ctx.show_text(line)
            ctx.stroke()
            yshift += self.font_size
            self.post_draw(ctx)
        h = yshift
        return Rect(x, y, w, h)


class Image(Drawable):
    def __init__(self, src, *args, **kwargs):
        super(Image, self).__init__(*args, **kwargs)
        self.src = None
        if isinstance(src, str):
            self.src = from_pil(PImage.open(src))

        # apparently there's no good way to figure out if an image is a PIL image ...
        if self.src is None:
            self.src = from_pil(src)

    def draw(self, ctx: cairo.Context):
        super(Image, self).draw(ctx)
        self.pre_draw(ctx)
        ctx.set_source_rgba(0, 0, 0, 0.0)

        # ctx.translate(-self.src.get_width() / 2, -self.src.get_height() / 2)

        ctx.rectangle(0, 0, self.src.get_width(), self.src.get_height())
        ctx.set_source_surface(self.src)
        ctx.clip()
        ctx.paint()

        self.post_draw(ctx)
        return Rect(0, 0, self.src.get_width(), self.src.get_height())


class Shape(Drawable):
    def __init__(self, stroke_width=1, fill_color=None, *args, **kwargs):
        super(Shape, self).__init__(*args, **kwargs)
        # assert fill_color is None
        self.fill_color = Color.new(fill_color) if fill_color else None
        self.stroke_width = stroke_width

    def draw(self, ctx: cairo.Context):
        pass


class Circle(Shape):
    def __init__(self, radius, *args, **kwargs):
        super(Circle, self).__init__(*args, **kwargs)
        self.radius = radius

    def draw(self, ctx: cairo.Context):
        self.pre_draw(ctx)
        ctx.set_line_width(self.stroke_width)
        ctx.arc(0, 0, self.radius, 0, math.pi * 2)
        if self.fill_color:
            ctx.set_source_rgba(*(self.fill_color.tup))
            ctx.fill_preserve()
            ctx.set_source_rgba(*(self.color.tup))
            ctx.stroke()
        else:
            ctx.stroke()
        self.post_draw(ctx)
