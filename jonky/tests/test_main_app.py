from jonky import Jonky
from jonky.drawable import Text, Position, Image


class Test(Jonky):
    def __init__(self, *args, **kwargs):
        super(Test, self).__init__(*args, **kwargs)
        self.items.extend(
            [
                Image(None).set_position(500, 500),
                Text("mononoki", 150, "hey", color=(0.5, 0.5, 0.5)).set_position(
                    200, 200
                ),
                Text("mononoki", 100, "hey", color=(1, 0.5, 0.5)).set_position(350, 350),
            ]
        )

    # def draw(self):
    #     super(Test, self).draw()
    #     print(f"yeah boi {self.i}")
    #     self.i += 1


if __name__ == "__main__":
    Test(period_in_sec=0.01).run()

# import cairo

# with cairo.SVGSurface("/tmp/meep.svg", 500, 500) as surface:
#     context = cairo.Context(surface)
#     Text("mononoki", 50, "hey", color=(0.5, 0.5, 0.5), position=Position(200, 200, False)).draw(context)
