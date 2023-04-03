from .drawable import Group, Packing, Color
from .jonky_main import JonkyImage


def make_jonky_grids(items_in, columns, rows, vertical_spacing=0, horizontal_spacing=0):
    items = [i for i in items_in]
    out = []
    i = 0
    while items:
        i += 1
        print(i)
        grp_outer = Group([], packing=Packing.VERTICAL, pack_padding=vertical_spacing)
        for j in range(rows):
            grp = Group([], packing=Packing.HORIZONTAL, pack_padding=horizontal_spacing)
            for i in range(columns):
                if not items:
                    continue
                grp.nodes.append(items.pop(0))
            if grp.nodes:
                grp_outer.nodes.append(grp)
        if grp_outer.nodes:
            out.append(grp_outer)
    return out


import matplotlib.pyplot as plt


def jshow(element, ret_only=False):
    ji = JonkyImage(1, 1, [element], background_color=Color.named("white"))
    r = element.draw(ji.cairo_context)
    ji = JonkyImage(
        int(r.x + r.w*(1.2)), int(r.y + r.h*(1.2)), [element.set_pose(r.w*0.1, r.h*0.1)], background_color=Color.named("white")
    )
    ji.draw()
    return ji.to_numpy()
    # out = Img(ji.to_numpy(), rgb=True)
    # if not ret_only:
    #     out.show()
    # return out
