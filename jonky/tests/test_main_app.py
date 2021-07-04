from libjari.jpath import JPath
from jonky import Jonky
from jonky.drawable import (
    Text,
    Pose,
    Image,
    Group,
    Packing,
    Circle,
    BakedGroup,
    Arc,
    Polygon,
    Color,
    Rectangle,
    PangoText
)
from jonky.widgets import DigitalClock, TimeDial, DayCal
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
                    PImage.open(JPath.from_home("Downloads/wapa/thumb1000.jpg").str).filter(
                        filter=ImageFilter.GaussianBlur(5)
                    )
                ),
                Text(
                    "Sans Serif",
                    20,
                    "Theree once was a\nship that took to see",
                    color="black",
                )
                .set_pose(250, 350)
                .set_pose_transformer(transform_pose),
                Group(
                    [
                        DigitalClock(
                            "US/Pacific", "Sans Serif", 30, "Office", color="white"
                        ),
                        DigitalClock("Europe/Berlin", "Sans Serif", 30, "Local"),
                    ],
                    Packing.VERTICAL,
                    10,
                ).set_pose(400, 100, 45),
                Group(
                    [DigitalClock("US/Eastern", "Sans Serif", 30, "Dallan")]
                    + [
                        Image(path.str)
                        for path in JPath.from_home("Pictures").glob_list("tag*png")
                    ],
                    Packing.VERTICAL,
                ).set_pose(0, 500),
                TimeDial(150, 20).set_pose(500, 500),
                TimeDial(180, 20).set_pose(500, 500, 90),
                DayCal(900, 300, 1, color=Color.named("white", 1.0)).set_pose(
                    1500, 100
                ),
                Rectangle(
                    300, 100, 10, 5, color="white", fill_color=Color.named("blue", 0.5)
                ).set_pose(100, 100),
                PangoText("Sans Serif", 15, "heyhey").set_pose(200, 200)
            ]
        )


if __name__ == "__main__":
    Test(period_in_sec=1, target_size=(1920, 1080)).run()
