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
import copy
import errno
import os
import math

# Some sketchy global configs
desired_max_tiles = 100
tile_target_width = 500
tile_target_height = 500


def highlight_file(style, filename):
    with open(filename) as f:
        code_txt = f.read()
        lexer = guess_lexer_for_filename(filename, code_txt)
        font_name = "Ubuntu Mono"
        formatter = JpgImageFormatter(font_name=font_name, style=style)
        return Image.open(io.BytesIO(highlight(code_txt, lexer, formatter)))


def glitch_image(image, amount_glitch, glitch_itr):
    # Note: Image warns us to use save with BytesIO instead
    # TODO: fix
    buff = io.BytesIO()
    image.save(buff, "jpeg")
    image_array = bytearray(buff.getvalue())
    seed = random.randint(0, 99)

    # We set iterations to 3 so we can verify each itr hasn't fucked
    # the world otherwise glitch_bytes could go a bit extreme.
    jpeg = jpglitch.Jpeg(image_array, amount_glitch, seed, iterations=3)
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
    offset_range = 50
    # crop takes (left, upper, right, lower)-tuple.
    source_size = img.size
    print("Source image size {0}".format(source_size))
    ret = []
    # Generate tiles iteratively with some skew
    for w in range(int(math.ceil(source_size[0] / tile_target_width))):
        for h in range(int(math.ceil(source_size[1] / tile_target_height))):
            x_offset = min(
                source_size[0] - tile_target_width,
                (random.randint(0, offset_range) +
                 source_size[0] - ((w + 1) * tile_target_width)))
            y_offset = min(
                source_size[1] - tile_target_height,
                (random.randint(0, offset_range) +
                 source_size[1] - ((h + 1) * tile_target_height)))
            print("Generating image for ({0},{1}) with offsets ({2},{3})".format(
                w, h, x_offset, y_offset))
            x0 = x_offset + (w * tile_target_width)
            y0 = y_offset + (h * tile_target_height)
            x1 = x_offset + ((w + 1) * tile_target_width)
            y1 = y_offset + ((h + 1) * tile_target_height)
            ret.append(img.crop((x0, y0, x1, y1)))
    # Generate 10 random tiles from "somewhere" in the image
    num_tiles = 10
    for _ in range(num_tiles):
        x0 = random.randint(0, source_size[0] - tile_target_width)
        y0 = random.randint(0, source_size[1] - tile_target_height)

        x1 = x0 + tile_target_width
        y1 = y0 + tile_target_height

        ret.append(img.crop((x0, y0, x1, y1)))
    return random.sample(ret, min(desired_max_tiles, len(ret)))


def build_tiles(filenames,
                style,
                amount_glitch,
                glitch_itr):
    highlighted = map(lambda filename: highlight_file(
        style, filename), filenames)
    ocropped = map(tileify, highlighted)
    print("cropped...")
    cropped = []
    for c in ocropped:
        for i in c:
            cropped.append(i)
    print("compacted to {0}".format(cropped))
    glitched_tiled = map(
        lambda img: glitch_image(img, amount_glitch, glitch_itr),
        cropped)
    glitched = map(lambda img: glitch_image(
        img, amount_glitch, glitch_itr), highlighted)
    return (highlighted, glitched, cropped, glitched_tiled)

#Front(Center) : 1487 x 4796 or Higher
#Front Left(Center) : 1053 x 4780 or Higher
#Front Right(Center) : 1053 x 4780 or Higher
#Back Right(Center) : 878 x 4803 or Higher
#Sleeve Left(Center) : 1775 x 2140 or Higher
#Pocket Right(Center) : 1067 x 704 or Higher
#Back Left(Center) : 881 x 4818 or Higher
#Back Rightside(Center) : 1039 x 4803 or Higher
#Sleeve Right(Center) : 1775 x 2140 or Higher
#Pocket Left(Center) : 1067 x 703 or Higher
#Back Leftside(Center) : 1039 x 4803 or Higher
def build_image(filenames,
                style="paraiso-dark",
                amount_glitch=75,
                glitch_itr=6,
                percent_original=10,
                dress_piece_dims=[
                    ("front", (1487, 4796)),
                    ("front_left", (1053, 4780)),
                    ("front_right", (1053, 4780)),
                    ("back_right", (878, 4803)),
                    ("sleeve_left", (1775, 2140)),
                    ("pocket_right", (1067, 704)),
                    ("back_left", (881, 4818)),
                    ("back_rightside", (1039, 4803)),
                    ("sleeve_right", (1775, 2140)),
                    ("pocket_left", (1067, 703)),
                    ("back_leftside", (1039, 4803))]):
    (highlighted, glitched, cropped, glitched_tiled) = build_tiles(
        filenames, style, amount_glitch, glitch_itr)
    num_tiles = len(cropped)

    def random_tile():
        tile_idx = random.randint(0, num_tiles - 1)
        if random.randint(0, 100) < percent_original:
            return cropped[tile_idx]
        else:
            return glitched_tiled[tile_idx]

    def make_piece(name_dim):
        """Make some glitched code combined for some specific dimensions"""
        dim = name_dim[1]
        img = Image.new('RGB', dim)
        for i in range(0, dim[0], tile_target_width):
            for j in range(0, dim[1], tile_target_height):
                img.paste(random_tile(), (i, j))
        return (name_dim[0], img)

    pieces = map(make_piece, dress_piece_dims)

    return (pieces, highlighted, glitched, cropped, glitched_tiled)


def make_if_needed(target_dir):
    """Make a directory if it does not exist"""
    try:
        os.mkdir(target_dir)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass


def save_imgs(target_dir, imgs, ext):
    idx = 0
    make_if_needed(target_dir)
    for img in imgs:
        idx = idx + 1
        filename = "{0}/{1}.{2}".format(target_dir, idx, ext)
        if type(img) is tuple:
            filename = "{0}/{1}.{2}".format(target_dir, img[0], ext)
            img[1].save(filename)
        else:
            img.save(filename)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Process some code')
    parser.add_argument('--files', type=str, default=["gen.py"],
                        nargs="*",
                        help="file names to process")
    parser.add_argument('--output', type=str, default="out",
                        nargs="?",
                        help="output directory")
    parser.add_argument('--extension', type=str, default="png",
                        nargs="?",
                        help="output extension")
    args = parser.parse_args()
    make_if_needed(args.output)
    (processed, highlighted, glitched, cropped,
     glitched_tiled) = build_image(args.files)
    save_imgs(args.output + "/processed", processed, args.extension)
    save_imgs(args.output + "/highlighted", highlighted, args.extension)
    save_imgs(args.output + "/glitched", glitched, args.extension)
    save_imgs(args.output + "/cropped", cropped, args.extension)
    save_imgs(args.output + "/glitched_tiled", glitched_tiled, args.extension)
