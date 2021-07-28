from jonky.drawable import (
    Text,
    Drawable,
    Group,
    Arc,
    Color,
    Rect,
    Polygon,
    Rectangle,
    Packing,
    Image,
    PangoText,
    Circle,
)
from jonky.widget_helpers import datetime_to_string, draw_ring, ampm
import maya
import time
import random
from bash import bash
import os
from orgparse import load as orgload
from PIL import Image as PImage
from libjari.jpath import JPath
from datetime import datetime


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


class DigitalClock(PangoText):
    def __init__(
        self,
        timezone,
        font,
        font_size,
        width=1000,
        show_seconds=False,
        suffix="",
        *args,
        **kwargs,
    ):
        self.timezone = timezone
        self.suffix = suffix
        self.show_seconds = show_seconds
        super(DigitalClock, self).__init__(font, font_size, self.text, *args, **kwargs)

    @property
    def text(self):
        m = maya.when("now").datetime(to_timezone=self.timezone)
        return datetime_to_string(m, self.show_seconds) + " " + self.suffix

    @text.setter
    def text(self, val):
        pass


class TimeDial(Group):
    def __init__(self, radius, width, *args, **kwargs):
        super(TimeDial, self).__init__(draw_ring(radius, width), *args, **kwargs)
        self.radius = radius

    def draw(self, ctx, do_xform=True):
        return super(TimeDial, self).draw(ctx, do_xform)


def make_scaler(max_val, intify=False):
    def scaler(frac):
        out = max_val * frac
        if intify:
            out = int(out)
        return out

    return scaler


class ConcirCal(Group):
    def __init__(self, radius, width, timezone, offsets, *args, **kwargs):
        super(ConcirCal, self).__init__(*args, **kwargs)
        bg_col = Color.named("black", 0.4)
        self.nodes.append(Circle(radius + width * 2.0, color=bg_col, fill_color=bg_col))
        self.nodes.append(TimeDial(radius, width))
        for i, ofs in enumerate(offsets):
            self.nodes.append(
                TimeDial(radius + (i+1)*width * 1.5, width).set_pose(yaw=-ofs * 15)
            )
        s = 3
        self.nodes.append(
            Polygon(
                [(0, 0), (-(radius - width / 2), s), (-(radius - width / 2), -s)],
                stroke_width=1,
                color=Color.named("white", 0.6),
                fill_color=Color.named("white", 0.6),
            )
        )
        self.timezone = timezone

    def draw(self, ctx):
        m = maya.when("now").datetime(to_timezone=self.timezone)
        hour_val = m.hour + m.minute / 60
        angle = 360 / 24 * (hour_val) - 9 * 15
        self.nodes[-1].set_pose(yaw=angle)
        return super(ConcirCal, self).draw(ctx)


class LineWithText(Group):
    def __init__(self, font, font_size, text, width, stroke_width, *args, **kwargs):
        self.nodes = []
        super(LineWithText, self).__init__(*args, **kwargs)
        self.width = width
        self.stroke_width = stroke_width
        self.text = PangoText(
            font, font_size, text, color=self.color, width=self.width, alignment="right"
        ).set_pose(x=-self.stroke_width * 4)
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
        r = min(corner_radius, width / 2, height / 2)
        self.text = PangoText(
            font, font_size, text, width=width, color=self.color
        ).set_pose(r + stroke_width, font_size)
        self.nodes.append(self.text)


class DayCal(Group):
    def __init__(
        self,
        height,
        width,
        stroke_width,
        font,
        nodes=None,
        time_function=None,
        timezone="",
        *args,
        **kwargs,
    ):
        super(DayCal, self).__init__([], *args, **kwargs)
        assert timezone != "", "Must set timezone"
        self.tz = timezone
        self.height = height
        self.width = width
        _s = make_scaler(self.height)
        self.font = font
        self._s = _s
        self.side_lines = [
            Rectangle(
                width,
                height,
                10,
                stroke_width,
                color=self.color,
                fill_color=Color.named("black", 0.65),
            )
        ]
        self.stroke_width = stroke_width
        self.lines = [
            LineWithText(
                self.font,
                self.height * 0.02,
                str(i),
                self.width,
                stroke_width,
                color=self.color,
            ).set_pose(y=_s(i * 0.1))
            for i in range(40)
        ]

        self.events = []

        self.time_function = (
            time_function if time_function is not None else (lambda: time.time())
        )

        self.update_events()

    def update_events(self):
        cal = str(
            bash(
                f"gcalcli --calendar {os.environ['JONKY_EMAIL_ADDRESS']} agenda --details=length --tsv "
                + maya.when("yesterday").datetime().strftime("%Y-%m-%d")
            )
        )
        res = [line.split("\t") for line in cal.split("\n")]
        event_times = []
        for r in res:
            event_times.append(
                (
                    maya.parse(r[0] + " " + r[1], timezone=self.tz).epoch,
                    maya.parse(r[2] + " " + r[3], timezone=self.tz).epoch,
                    r[-1].replace("&", "&amp;"),
                )
            )

            if (event_times[-1][1] - event_times[-1][0]) == 3600 * 24:
                event_times[-1] = (
                    event_times[-1][0],
                    event_times[-1][0] + 3600,
                    event_times[-1][-1],
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

        l = self.lines[i]
        l.text.color = Color.named("red")
        l.line.color = Color.named("red")
        l.line.stroke_width = 2
        l.set_pose(y=_s(ht_xform(0.5)))
        l.text.font_size = _s(ht_font(0.5)) * 0.01
        l.text.text = ""
        final_lines.append(l)
        rects = []

        zero_time = timestamp - 12 * 3600
        end_time = timestamp + 12 * 3600

        for et in self.events:
            if not (zero_time < et[0] < end_time or zero_time < et[1] < end_time):
                continue
            start_loc = (et[0] - zero_time + 30 * 60) / th
            end_loc = (et[1] - zero_time + 30 * 60) / th

            font_size = _s(start_loc) * 0.01
            if start_loc < 0.2 or start_loc > 0.8:
                continue
            start_loc = _s(ht_xform(start_loc))
            end_loc = _s(ht_xform(end_loc))
            rects.append(
                RectangleWithText(
                    self.width - self.stroke_width * 4,
                    end_loc - start_loc,
                    5,
                    self.font,
                    min((end_loc - start_loc) * 0.25, self.height * 0.008),
                    et[-1],
                    stroke_width=self.stroke_width,
                    color="E8E9A1",
                    fill_color=Color.named("white", 0.4),
                ).set_pose(self.stroke_width * 2, y=start_loc)
            )

        self.nodes = self.side_lines + final_lines + rects
        return super(DayCal, self).draw(ctx)


tsize = 20


def datetime_strip_minutes_seconds(date: datetime):
    return datetime(date.year, date.month, date.day)


_ds = datetime_strip_minutes_seconds


def check():
    return Image(PImage.open(JPath.from_home("Downloads/check-circle-solid.png").str))


def cross():
    return Image(PImage.open(JPath.from_home("Downloads/times-circle-solid.png").str))


def sched():
    return Image(PImage.open(JPath.from_home("Downloads/calendar-solid.png").str))


def exclaim():
    return Image(PImage.open(JPath.from_home("Downloads/exclamation-solid.png").str))


class OrgHabits(Group):
    def __init__(self, filename, font, size=20, width=350, *args, **kwargs):
        super(OrgHabits, self).__init__(*args, **kwargs)
        self.filename = filename
        self.packing = Packing.VERTICAL
        self.font = font
        self.size = size
        self.width = width
        self.pack_padding = size / 4
        self.i = 0

    def draw(self, ctx):
        self.i += 1
        self.nodes = []
        hb = orgload(self.filename)
        seen = {}
        for child in hb.children:
            if child.heading in seen:
                continue
            seen[child.heading] = True
            today = _ds(datetime.today())
            dones = [((_ds(d.start) - today).days) for d in child.repeated_tasks]
            alls = list(range(-5, 6, 1))
            other_group = []
            for i, a in enumerate(alls):
                if a in dones:
                    other_group.append(check())
                else:
                    ims = []
                    if a < 0:
                        le_im = cross
                    else:
                        le_im = sched
                    ims.append(le_im())
                    if a == 0:
                        le_im = exclaim
                        ims.append(le_im())
                    other_group.append(Group(ims))
            self.nodes.append(
                PangoText(
                    self.font,
                    self.size,
                    child.heading,
                    width=self.width,
                    color=self.color,
                )
            )
            self.nodes.append(
                Group(other_group, packing=Packing.HORIZONTAL).set_scale(
                    self.size / 100
                )
            )
        return super(OrgHabits, self).draw(ctx)


class Dial(Group):
    def __init__(self, radius, stroke_width, val=0, name="", *args, **kwargs):
        super(Dial, self).__init__(*args, **kwargs)
        self.radius = radius
        self.nodes.append(
            Arc(radius, 90, 360, stroke_width=stroke_width, *args, **kwargs)
        )
        self.nodes.append(
            Arc(
                radius * 0.5, 90, 360, stroke_width=stroke_width * 3, *args, **kwargs
            ).set_alpha(0.2)
        )
        for angle in range(90, 361, 10):
            self.nodes.append(
                Polygon(
                    [(radius * 0.85, 0), (radius + stroke_width / 2, 0)],
                    stroke_width=stroke_width / 3,
                    *args,
                    **kwargs,
                ).set_pose(yaw=angle)
            )

        self.nodes.append(
            Group(
                [
                    Polygon(
                        [
                            (radius * 0.8, 0),
                            (-radius * 0.25, radius * 0.05),
                            (-radius * 0.25, -radius * 0.05),
                            (radius * 0.8, 0),
                        ],
                        color="#a80300",
                        fill_color="#a80300",
                    ),
                    Circle(
                        radius * 0.05,
                        color="#a80300",
                        stroke_width=stroke_width * 0.4,
                        fill_color="black",
                    ),
                ]
            )
        )
        self.nodes.append(
            PangoText("", radius * 0.3, "", color="white").set_pose(
                radius * 0.1, radius * 0.2
            )
        )
        self.val = val
        self.name = name

    def draw(self, ctx):
        self.nodes[-2].set_pose(yaw=90 + self.val * (360 - 90))
        self.nodes[-1].text = f"{int(self.val*100)}%\n{self.name}"
        return super(Dial, self).draw(ctx)
