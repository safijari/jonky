from jonky.jonky import JonkyImage
from jonky.drawable import Group, Packing
from jonky.widgets import DigitalClock

if __name__ == "__main__":
    items = [
        Group(
            [
                DigitalClock(
                    "Europe/Berlin", "mononoki", 50, suffix="Local", color="white"
                ),
                DigitalClock(
                    "US/Pacific", "mononoki", 50, suffix="Office", color="gray"
                ),
            ],
            Packing.VERTICAL,
            10,
        ),
    ]
    JonkyImage(500, 300, items, scale=2).draw().save("test.png")
