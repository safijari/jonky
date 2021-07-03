from jonky.drawable import Text, Drawable, Group, Arc, Color, Rect
import maya


def datetime_to_string(dt):
    am = "am"
    h = dt.hour
    if h == 0:
        h = 12
    if h > 12:
        h = h % 12
        am = "pm"
    return f"{str(h).zfill(2)}:{str(dt.minute).zfill(2)}:{str(dt.second).zfill(2)} {am}"


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


def _f(val1, val2, frac):
    return (val1 * frac) + val2 * (1 - frac)


def interpolate_col(c1, c2, frac):
    r1, g1, b1 = c1[:3]
    r2, g2, b2 = c2[:3]
    return (_f(r1, r2, frac), _f(g1, g2, frac), _f(b1, b2, frac))


def normalize_color(col):
    if any([c > 1 for c in col]):
        return [c / 255.0 for c in col]
    return col


def arc_with_start_end_colors(
    radius, start_deg, stop_deg, width, start_col, end_col, subdivision=1
):
    start_col = Color.new(start_col)
    end_col = Color.new(end_col)
    arcs = []
    for i in range(start_deg, stop_deg, subdivision):
        arcs.append(
            Arc(
                radius,
                i - subdivision / 6,
                i + subdivision + subdivision / 6,
                color=interpolate_col(
                    end_col.tup, start_col.tup, (i - start_deg) / (stop_deg - start_deg)
                ),
                stroke_width=width,
            )
        )

    return arcs


def draw_ring(radius, width):
    # background white bit
    arcs = []
    arcs.extend(arc_with_start_end_colors(radius, 0, 360, width + 5, "white", "white"))
    start_col = (165 * 0.5, 135 * 0.5, 0)
    end_col = (247, 227, 5)

    arcs.extend(
        arc_with_start_end_colors(radius, 180 - 25, 180 + 45, width, start_col, end_col)
    )

    start_col = end_col
    end_col = (78, 84, 129)

    arcs.extend(
        arc_with_start_end_colors(radius, 180 + 45, 360 - 25, width, start_col, end_col)
    )

    start_col = end_col
    end_col = (0.1, 0.1, 0.1)

    arcs.extend(
        arc_with_start_end_colors(radius, 360 - 25, 360 + 30, width, start_col, end_col)
    )

    start_col = end_col

    arcs.extend(
        arc_with_start_end_colors(radius, 30, 90 + 25, width, start_col, end_col)
    )

    start_col = end_col
    end_col = (165 * 0.5, 135 * 0.5, 0)
    arcs.extend(
        arc_with_start_end_colors(radius, 90 + 25, 180 - 25, width, start_col, end_col)
    )

    width = width * 0.5

    def _arc(angle, expansion, color):
        return Arc(
            radius,
            angle - expansion,
            angle + expansion,
            stroke_width=width,
            color=color,
        )

    for i in range(0, 360, 15):
        arcs.append(_arc(i, 0.25, "white"))

    arcs.append(_arc(180, 0.5, "green"))
    arcs.append(_arc(180 + 120, 0.5, "red"))
    arcs.append(_arc(180 + 225, 0.5, "blue"))
    return arcs


class TimeDial(Group):
    def __init__(self, radius, width, *args, **kwargs):
        super(TimeDial, self).__init__(draw_ring(radius, width), *args, **kwargs)
        self.radius = radius

    def draw(self, ctx, do_xform=True):
        super(TimeDial, self).draw(ctx, do_xform)
        return Rect(0, 0, 1000, 1000)
