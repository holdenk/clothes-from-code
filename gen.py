#!/usr/bin/env python
import pygments
import random
from PIL import Image
import jpglitch
from pygments import highlight
from pygments.lexers import guess_lexer_for_filename
from pygments.formatters import JpgImageFormatter
import io
import tempfile

font_name = "Courier New"
formatter = JpgImageFormatter(font_name=font_name)

def highlight_file(filename):
    with open(filename) as f: code_txt = f.read()
    lexer = guess_lexer_for_filename(filename, code_txt)
    return Image.open(io.BytesIO(highlight(code_txt, lexer, formatter)))

def glitch_image(image, amount_glitch, glitch_itr):
    # Note: Image warns us to use save with BytesIO instead
    # TODO: fix
    buff = io.BytesIO()
    image.save(buff, "jpeg")
    image_array = bytearray(buff.getvalue())
    seed = random.randint(0, 99)

    # We set iterations to 3 so we can verify each itr hasn't fucked the world otherwise glitch_bytes could go a bit extreme.
    jpeg = jpglitch.Jpeg(image_array, amount_glitch, seed, iterations = 3)
    img_bytes = jpeg.new_bytes
    # Gltich the image until max itrs, or stop if it doesn't open anymore
    for i in range(glitch_itr):
        print("Glitching {0}th time".format(i))
        jpeg.glitch_bytes()
        try:
            stream = io.BytesIO(jpeg.new_bytes)
            im = Image.open(stream)
            im.save(tempfile.mkstemp("glitch.jpg")[1])
            img_bytes = jpeg.new_bytes
        except IOError:
            break
    return Image.open(io.BytesIO(img_bytes))

def tileify(img):
    """
    Takes in an image and produces several smaller tiles.
    Tiles are uniform in shape but may not be uniformly cut.
    """
    target_width = 500
    target_height = 500
    offset_range = 50
    # crop takes (left, upper, right, lower)-tuple.
    source_size = img.size
    ret = []
    for w in range(source_size[0] / target_width):
        for h in range(source_size[1] / target_height):
            x_offset = min(random.randint(0, offset_range),
                           source_size[0] - ((w + 1) * target_width))
            y_offset = min(random.randint(0, offset_range),
                           source_size[1] - ((h + 1) * target_height))
            x0 = x_offset + (w * target_width)
            y0 = y_offset + (h * target_height)
            x1 = x_offset + ((w + 1) * target_width)
            y1 = y_offset + ((h + 1) * target_height)
            ret.append(img.crop((x0, y0, x1, y1)))
    return ret
    

def build_images(filenames,
                style="terminal",
                amount_glitch = 75,
                glitch_itr = 6):
    highlighted = map(highlight_file, filenames)
    ocropped = map(tileify, highlighted)
    print("cropped...")
    cropped = []
    for c in ocropped:
        for i in c:
            cropped.append(i)
    print("compacted to {0}".format(cropped))
    glitched = map(lambda img: glitch_image(img, amount_glitch, glitch_itr),
                   cropped)
    return (cropped, glitched)


def build_image(filenames,
                style="terminal",
                amount_glitch = 75,
                glitch_itr = 6,
                precent_original = 10):
    imgs = build_images(filenames, style, amount_glitch, glitch_tr)
    
