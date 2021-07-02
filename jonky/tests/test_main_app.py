from jonky import Jonky
from jonky.drawable import Text, Pose, Image
from PIL import Image as PImage
from PIL import ImageFilter


class Test(Jonky):
    def __init__(self, *args, **kwargs):
        super(Test, self).__init__(*args, **kwargs)
        self.items.extend(
            [
                Image(PImage.open("/home/jari/Downloads/wapa/thumb0001.jpg").filter(filter=ImageFilter.GaussianBlur(5))),
                Text("mononoki", 150, "hey", color=(0.5, 0.5, 0.5)).set_pose(
                    200, 200
                ),
                Text("mononoki", 100, "hey", color=(1, 0.5, 0.5)).set_pose(350, 350),
            ]
        )

if __name__ == "__main__":
    Test(period_in_sec=1, target_size=(1920, 1080)).run()

# import cairo

# with cairo.SVGSurface("/tmp/meep.svg", 500, 500) as surface:
#     context = cairo.Context(surface)
#     Text("mononoki", 50, "hey", color=(0.5, 0.5, 0.5), pose=Position(200, 200, False)).draw(context)
