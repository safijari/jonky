from jonky.drawable import Text, Drawable, Group, Arc, Color, Rect, Polygon
from jonky.widget_helpers import datetime_to_string, draw_ring, ampm
import maya
import time
import random


def fn(x):
    s = 3
    sgn = -1
    if s % 2 == 1:
        sgn = 1
    if x < 0.5:
        return -(((x) * 2) ** s) + 1
    return -(sgn * ((x - 1.0) * 2) ** s + 1)


def ht_xform(x):
    return (1 - fn(x)) / 2


def fn_font(x):
    s = 1
    sgn = -1
    if s % 2 == 1:
        sgn = 1
    if x < 0.5:
        return -(((x) * 2) ** s) + 1
    return ((x - 1.0) * 2) ** s + 1


def ht_font(x):
    return float(1 - fn_font(x))


class DigitalClock(Text):
    def __init__(self, timezone, font, font_size, suffix="", *args, **kwargs):
        self.timezone = timezone
        self.suffix = suffix
        super(DigitalClock, self).__init__(font, font_size, self.text, *args, **kwargs)

    @property
    def text(self):
        m = maya.when("now").datetime(to_timezone=self.timezone)
        return datetime_to_string(m) + " " + self.suffix

    @text.setter
    def text(self, val):
        pass


class TimeDial(Group):
    def __init__(self, radius, width, *args, **kwargs):
        super(TimeDial, self).__init__(draw_ring(radius, width), *args, **kwargs)
        self.radius = radius

    def draw(self, ctx, do_xform=True):
        super(TimeDial, self).draw(ctx, do_xform)
        return Rect(0, 0, 1000, 1000)


def make_scaler(max_val, intify=False):
    def scaler(frac):
        out = max_val * frac
        if intify:
            out = int(out)
        return out

    return scaler


class LineWithText(Group):
    def __init__(self, font, font_size, text, width, stroke_width, *args, **kwargs):
        self.nodes = []
        super(LineWithText, self).__init__(*args, **kwargs)
        self.width = width
        self.stroke_width = stroke_width
        self.text = Text(
            font, font_size, text, on_bottom=True, color=self.color
        ).set_pose(x=self.stroke_width * 2, y=-self.stroke_width * 3)
        self.line = Polygon(
            [(0, 0), (width, 0)], stroke_width=stroke_width, color=self.color
        )
        self.nodes = [self.text, self.line]


class DayCal(Group):
    def __init__(
        self,
        height,
        width,
        stroke_width,
        nodes=None,
        time_function=None,
        *args,
        **kwargs
    ):
        super(DayCal, self).__init__([], *args, **kwargs)
        self.height = height
        self.width = width
        _s = make_scaler(self.height)
        self._s = _s
        self.side_lines = []
        self.side_lines.append(
            Polygon(
                [(0, 0), (0, self.height)], stroke_width=stroke_width, color=self.color
            ),
        )
        self.side_lines.append(
            Polygon(
                [(self.width, 0), (self.width, self.height)],
                stroke_width=stroke_width,
                color=self.color,
            ),
        )
        self.lines = [
            LineWithText(
                "mononoki",
                self.height * 0.02,
                str(i),
                self.width,
                stroke_width,
                color=self.color,
            ).set_pose(y=_s(i * 0.1))
            for i in range(40)
        ]

        def time_function():
            try:
                st = time_function.start_time
            except Exception:
                time_function.start_time = time.time()
                st = time_function.start_time
            return (time.time() - st) * 60 * 60 + st

        self.time_function = (
            time_function if time_function is not None else (lambda: time.time())
        )

    def draw(self, ctx):
        _s = self._s
        final_lines = []
        timestamp = self.time_function()
        le_time = maya.Datetime.fromtimestamp(timestamp)
        offset = le_time.minute * 60
        hr = le_time.hour

        th = 25 * 3600

        i = 0
        res = 0.5 - offset / th
        while res > 0:
            l = self.lines[i]
            l.set_pose(y=_s(ht_xform(res)))
            l.text.text = ampm(hr)
            l.text.font_size = _s(ht_font(res)) * 0.02
            final_lines.append(l)
            res -= 3600 / th
            hr -= 1
            i += 1

        hr = le_time.hour + 1
        res = 0.5 + (3600 - offset) / th
        while res < 1.3:
            l = self.lines[i]
            l.set_pose(y=_s(ht_xform(res)))
            l.text.text = ampm(hr)
            l.text.font_size = _s(ht_font(res)) * 0.02
            final_lines.append(l)
            res += 3600 / th
            hr += 1
            i += 1

        self.nodes = self.side_lines + final_lines
        super(DayCal, self).draw(ctx)
