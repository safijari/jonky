# from libjari.jdraw import convert_color
import math
from dataclasses import dataclass
import cairo

# ccf = convert_color_float

@dataclass
class Position:
    x: float
    y: float
    is_percent: bool

class Drawable:
    """Documentation for Drawable

    """
    def __init__(self, position=None, color=None):
        if color is None:
            color = (0, 0, 0)
        # color = ccf(color)
        self.color = color
        if position is None:
            position = Position(0, 0, False)
        assert not position.is_percent
        self.position = position

    def set_position(self, x, y):
        self.position.x = x
        self.position.y = y
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
        self.i = 0


    def draw(self, ctx):
        self.i += 1
        ctx.save()
        ctx.select_font_face(self.font)
        ctx.set_font_size(self.font_size)
        (x, y, width, height, dx, dy) = ctx.text_extents(self.text)
        ctx.set_source_rgb(*(self.color))
        ctx.translate(self.position.x, self.position.y)
        ctx.rotate(self.i * 0.1)
        ctx.translate(-x - width/2, -y - self.font_size/2)
        ctx.show_text(self.text)
        # ctx.move_to(self.position.x - x, self.position.y - y)
        # ctx.rotate(5)
        ctx.stroke()
        ctx.restore()

class Image(Drawable):
    def __init__(self, src, *args, **kwargs):
        super(Image, self).__init__(*args, **kwargs)
        self.i = 0
        self.src = cairo.ImageSurface.create_from_png("/home/jari/Pictures/tag1.png")

    def draw(self, ctx: cairo.Context):
        self.i += 1
        ctx.save()
        ctx.set_source_rgba(0, 0, 0, 0.0)
        ctx.translate(self.position.x, self.position.y)
        ctx.rotate(self.i * 0.01)
        ctx.translate(-self.src.get_width() / 2, -self.src.get_height()/2)
        ctx.rectangle(0, 0, self.src.get_width(), self.src.get_height())
        ctx.set_source_surface(self.src)
        ctx.clip()
        ctx.paint()
        ctx.restore()