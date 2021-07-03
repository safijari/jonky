import PIL.Image as Image
import cairo
import math


def from_pil(im, alpha=1.0, format=cairo.FORMAT_ARGB32):
    """
    :param im: Pillow Image
    :param alpha: 0..1 alpha to add to non-alpha images
    :param format: Pixel format for output surface
    """
    assert format in (cairo.FORMAT_RGB24, cairo.FORMAT_ARGB32), (
        "Unsupported pixel format: %s" % format
    )
    if "A" not in im.getbands():
        im.putalpha(int(alpha * 256.0))
    arr = bytearray(im.tobytes("raw", "BGRa"))
    surface = cairo.ImageSurface.create_for_data(arr, format, im.width, im.height)
    return surface


def _rad(deg):
    return deg * math.pi / 180
