from libjari.colors import convert_color_float
import math
from dataclasses import dataclass
import cairo
from jonky.helpers import from_pil
from PIL import Image as PImage
import PIL

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


class Drawable:
    """Documentation for Drawable

    """

    def __init__(self, pose=None, color=None):
        if color is None:
            color = (0, 0, 0)
        color = _ccf(color)
        print(color)
        self.color = color
        if pose is None:
            pose = Pose()
        self.pose = pose

    def set_pose(self, x=None, y=None, yaw=None):
        if x:
            self.pose.x = x
        if y:
            self.pose.y = y
        if yaw:
            self.yaw = yaw
        return self

    def draw(self, ctx):
        pass


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
        ctx.save()
        ctx.select_font_face(self.font)
        ctx.set_font_size(self.font_size)
        (x, y, width, height, dx, dy) = ctx.text_extents(self.text)
        ctx.set_source_rgb(*(self.color))

        ctx.translate(self.pose.x, self.pose.y)
        ctx.rotate(self.pose.yaw_rad)
        # ctx.translate(-x - width / 2, -y - self.font_size / 2)

        ctx.show_text(self.text)
        ctx.stroke()
        ctx.restore()


class Image(Drawable):
    def __init__(self, src, *args, **kwargs):
        super(Image, self).__init__(*args, **kwargs)
        self.src = None
        if isinstance(src, str):
            self.src = from_pil(PImage.open(src))

        # apparently there's no good way to figure out if an image is a PIL image ...
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
