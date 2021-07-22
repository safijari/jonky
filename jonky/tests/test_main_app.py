from libjari.jpath import JPath
from jonky.jonky_main import JonkyTk
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
    PangoText,
    Spiral
)
from jonky.widgets import DigitalClock, TimeDial, DayCal, Dial
from PIL import Image as PImage
from PIL import ImageFilter
from libjari.jpath import JPath
import random
import psutil

import math


def transform_pose(pose, time):
    pose.x = math.sin(time) * 30
    pose.yaw = math.sin(time) * 30


if __name__ == "__main__":
    items = [
        Image(
            PImage.open(JPath.from_home("Downloads/wapa/thumb1000.jpg").str).filter(
                filter=ImageFilter.GaussianBlur(5)
            )
        ),
        Text(
            "Sans Serif", 20, "Theree once was a\nship that took to see", color="black",
        )
        .set_pose(250, 350)
        .set_pose_transformer(transform_pose),
        Group(
            [
                DigitalClock("US/Pacific", "Sans Serif", 30, "Office", color="white"),
                DigitalClock("Europe/Berlin", "Sans Serif", 30, "Local"),
            ],
            Packing.VERTICAL,
            10,
        ).set_pose(400, 100, 45),
        Group(
            [DigitalClock("US/Eastern", "Sans Serif", 30, "Dallan", show_seconds=True)]
            + [
                Image(path.str)
                for path in JPath.from_home("Pictures").glob_list("tag*png")
            ],
            Packing.VERTICAL,
        ).set_pose(0, 500),
        # TimeDial(150, 20).set_pose(500, 500),
        # TimeDial(180, 20).set_pose(500, 500, 90),
        # DayCal(900, 300, 1, color=Color.named("white", 1.0)).set_pose(
        #     1500, 100
        # ),
        Rectangle(
            300, 100, 10, 5, color="white", fill_color=Color.named("blue", 0.5)
        ).set_pose(100, 100),
        PangoText("Sans Serif", 15, "heyhey").set_pose(200, 200),
        Dial(200, 10, 0.5)
        .set_pose(200, 200)
        .set_updater(lambda self: psutil.cpu_percent() / 100, "val", 0.5),
        Spiral(0, 360*10, 50, 50 + 13 * 10, ccw=True, color="white", stroke_width=10).set_pose(500, 500)
    ]
    JonkyTk(500, 500, items, update_period=0.01, is_background=True)
