from libjari.colors import convert_color_float
import math
from dataclasses import dataclass
import cairo
from jonky.helpers import from_pil
from PIL import Image as PImage
import PIL
from enum import Enum

_ccf = convert_color_float


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
        if color is None:
            color = (0, 0, 0)
        color = _ccf(color)
        self.color = color
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

    def draw(self, ctx):
        ctx.save()
        ctx.translate(self.pose.x, self.pose.y)
        ctx.rotate(self.pose.yaw_rad)
        rect = Rect(self.pose.x, self.pose.y, 0, 0)
        for i, node in enumerate(self.nodes):
            if self.packing != Packing.NONE:
                if self.packing == Packing.VERTICAL:
                    node.set_pose(0, rect.h + i * self.pack_padding)
                if self.packing == Packing.HORIZONTAL:
                    node.set_pose(rect.w + i * self.pack_padding, 0)
            _rect = node.draw(ctx)
            rect.w += _rect.w
            rect.h += _rect.h
        ctx.restore()
        return rect


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
            ctx.save()
            ctx.select_font_face(self.font)
            ctx.set_font_size(self.font_size)
            (x, y, width, height, dx, dy) = ctx.text_extents(self.text)
            w = max(width, w)
            ctx.set_source_rgb(*(self.color))

            ctx.translate(self.pose.x, self.pose.y)
            ctx.rotate(self.pose.yaw_rad)
            ctx.translate(0, yshift)
            # ctx.translate(-x - width / 2, -y - self.font_size / 2)

            ctx.show_text(line)
            ctx.stroke()
            yshift += self.font_size
            ctx.restore()
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
        ctx.save()
        ctx.set_source_rgba(0, 0, 0, 0.0)

        ctx.translate(self.pose.x, self.pose.y)
        ctx.rotate(self.pose.yaw_rad)
        # ctx.translate(-self.src.get_width() / 2, -self.src.get_height() / 2)

        ctx.rectangle(0, 0, self.src.get_width(), self.src.get_height())
        ctx.set_source_surface(self.src)
        ctx.clip()
        ctx.paint()

        ctx.restore()
        return Rect(0, 0, self.src.get_width(), self.src.get_height())
