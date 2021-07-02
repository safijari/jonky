from jonky.drawable import Text
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
