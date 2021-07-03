from jonky import Jonky
from jonky.drawable import Text, Pose, Image, Group, Packing, Circle, BakedGroup
from jonky.widgets import DigitalClock
from PIL import Image as PImage
from PIL import ImageFilter
from libjari.jpath import JPath

import math


def transform_pose(pose, time):
    pose.x = math.sin(time) * 30
    pose.yaw = math.sin(time) * 30


class Test(Jonky):
    def __init__(self, *args, **kwargs):
        super(Test, self).__init__(*args, **kwargs)
        self.items.extend(
            [
                Image(
                    PImage.open("/home/jari/Downloads/wapa/thumb1000.jpg").filter(
                        filter=ImageFilter.GaussianBlur(5)
                    )
                ),
                Text(
                    "Ubuntu mono",
                    20,
                    "Theree once was a\nship that took to see",
                    color="black",
                )
                .set_pose(250, 350)
                .set_pose_transformer(transform_pose),
                BakedGroup(
                    [
                        DigitalClock(
                            "US/Pacific", "mononoki", 30, "Office", color="white"
                        ),
                        DigitalClock("Europe/Berlin", "mononoki", 30, "Local"),
                    ],
                    Packing.VERTICAL,
                    10,
                ).set_pose(400, 100, 45),
                Circle(100, stroke_width=10, color="black", fill_color="red").set_pose(
                    100, 100
                ),
                Group(
                    [
                        Image(path.str)
                        for path in JPath.from_home("Pictures").glob_list("tag*png")
                    ]
                    + [DigitalClock("US/Eastern", "mononoki", 30, "Dallan")],
                    Packing.VERTICAL,
                ).set_pose(0, 500),
            ]
        )


if __name__ == "__main__":
    Test(period_in_sec=0.01, target_size=(1920, 1080)).run()

# import cairo

# with cairo.SVGSurface("/tmp/meep.svg", 500, 500) as surface:
#     context = cairo.Context(surface)
#     Text("mononoki", 50, "hey", color=(0.5, 0.5, 0.5), pose=Position(200, 200, False)).draw(context)
