from jonky.drawable import Text, Drawable, Group, Arc, Color, Rect


def datetime_to_string(dt, show_seconds=True):
    am = "am"
    h = dt.hour
    if h == 0:
        h = 12
    elif h > 12:
        h = h % 12
        am = "pm"
    elif h == 12:
        am = "pm"
    oot = f"{str(h).zfill(2)}:{str(dt.minute).zfill(2)}"
    if show_seconds:
        oot += f":{str(dt.second).zfill(2)}"
    oot += f" {am}"
    return oot


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


def ampm(hr):
    hr = hr % 24
    if hr == 0:
        return f"{hr+12} am"
    if hr < 12:
        return f"{hr} am"
    if hr > 12:
        hr = hr - 12
    return f"{hr} pm"
