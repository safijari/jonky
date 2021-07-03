from jonky.drawable import Text, Drawable, Group, Arc, Color, Rect, Polygon, Rectangle
from jonky.widget_helpers import datetime_to_string, draw_ring, ampm
import maya
import time
import random
from bash import bash
import os


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


class RectangleWithText(Group):
    def __init__(
        self,
        width,
        height,
        corner_radius,
        font,
        font_size,
        text,
        stroke_width,
        *args,
        **kwargs,
    ):
        super(RectangleWithText, self).__init__(*args, **kwargs)
        self.nodes = [
            Rectangle(
                width, height, corner_radius, stroke_width=stroke_width, *args, **kwargs
            )
        ]
        self.text = Text(font, font_size, text, color=self.color).set_pose(
            corner_radius + stroke_width, corner_radius + stroke_width
        )
        self.nodes.append(self.text)


class DayCal(Group):
    def __init__(
        self,
        height,
        width,
        stroke_width,
        nodes=None,
        time_function=None,
        *args,
        **kwargs,
    ):
        super(DayCal, self).__init__([], *args, **kwargs)
        self.height = height
        self.width = width
        _s = make_scaler(self.height)
        self._s = _s
        self.side_lines = [Rectangle(width, height, 20, stroke_width, color=self.color)]
        self.stroke_width = stroke_width
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

        self.events = []
        self.update_events()

        self.time_function = (
            time_function if time_function is not None else (lambda: time.time())
        )

    def update_events(self):
        cal = str(
            bash(
                f"gcalcli --calendar {os.environ['JONKY_EMAIL_ADDRESS']} agenda --details=length --tsv"
            )
        )
        res = [line.split("\t") for line in cal.split("\n")]
        event_times = []
        for r in res:
            event_times.append(
                (
                    maya.parse(r[0] + " " + r[1], timezone="Europe/Berlin").epoch,
                    maya.parse(r[2] + " " + r[3], timezone="Europe/Berlin").epoch,
                    r[-1],
                )
            )
        self.events = event_times

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
        while res > 0.2:
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
        while res < 0.8:
            l = self.lines[i]
            l.set_pose(y=_s(ht_xform(res)))
            l.text.text = ampm(hr)
            l.text.font_size = _s(ht_font(res)) * 0.02
            final_lines.append(l)
            res += 3600 / th
            hr += 1
            i += 1

        rects = []

        zero_time = timestamp - 12 * 3600
        end_time = timestamp + 12 * 3600

        for et in self.events:
            if not (zero_time < et[0] < end_time or zero_time < et[1] < end_time):
                continue
            start_loc = (et[0] - zero_time) / th
            end_loc = (et[1] - zero_time) / th

            font_size = _s(start_loc) * 0.01
            if start_loc < 0.2 or start_loc > 0.8:
                continue
            start_loc = _s(ht_xform(start_loc))
            end_loc = _s(ht_xform(end_loc))
            # event_at(ht_xform(start_loc + 0.001), ht_xform(end_loc - 0.001))
            # text_at(ht_xform((start_loc + end_loc)/2), 0.1, et[-1])
            rects.append(
                # Rectangle(
                #     self.width - self.stroke_width * 4,
                #     end_loc - start_loc,
                #     5,
                #     color="blue",
                #     fill_color=Color.named("white", 0.2),
                # ).set_pose(self.stroke_width * 2, y=start_loc)
                RectangleWithText(
                    self.width - self.stroke_width * 4,
                    end_loc - start_loc,
                    5,
                    "mononoki",
                    min((end_loc - start_loc) * 0.5, self.height*0.05),
                    et[-1],
                    stroke_width=self.stroke_width,
                    color="blue",
                    fill_color=Color.named("white", 0.2),
                ).set_pose(self.stroke_width * 2, y=start_loc)
            )

        self.nodes = self.side_lines + final_lines + rects
        super(DayCal, self).draw(ctx)
