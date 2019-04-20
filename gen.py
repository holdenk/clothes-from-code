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


def build_tiles(filenames,
                style,
                amount_glitch,
                glitch_itr):
    highlighted = map(lambda filename: highlight_file(style, filename), filenames)
    ocropped = map(tileify, highlighted)
    print("cropped...")
    cropped = []
    for c in ocropped:
        for i in c:
            cropped.append(i)
    print("compacted to {0}".format(cropped))
    glitched_tiled = map(lambda img: glitch_image(img, amount_glitch, glitch_itr),
                   cropped)
    glitched = map(lambda img: glitch_image(img, amount_glitch, glitch_itr), highlighted)
    return (highlighted, glitched, cropped, glitched_tiled)


def build_image(filenames,
                style="paraiso-dark",
                amount_glitch=75,
                glitch_itr=6,
                percent_original = 10,
                dress_piece_dims = [
                    (878, 4803), (1487, 4796), (1053, 4780), (1775, 2140), (1067, 704),
                    (1775, 2140), (1067, 703), (881, 4818), (1039, 4803), (1039, 4803),
                    (1053, 4780)]):
    (highlighted, glitched, cropped, glitched_tiled) = build_tiles(filenames, style, amount_glitch, glitch_itr)
    num_tiles = len(cropped)
    def random_tile():
        tile_idx = random.randint(0, num_tiles - 1)
        if random.randint(0, 100) < percent_original:
            return cropped[tile_idx]
        else:
            return glitched_tiled[tile_idx]
    input_tile_width = 500
    input_tile_height = 500
    
    def make_piece(dim):
        """Make some glitched code combined for some specific dimensions"""
        img = Image.new('RGB', dim)
        for i in range(0, dim[0], input_tile_width):
            for j in range(0, dim[1], input_tile_height):
                img.paste(random_tile(), (i, j))
        return img

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
        idx = idx +1
        filename = "{0}/{1}.{2}".format(target_dir, idx, ext)
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
    (processed, highlighted, glitched, cropped, glitched_tiled) = build_image(args.files)
    save_imgs(args.output + "/processed", processed, args.extension)
    save_imgs(args.output + "/highlighted", highlighted, args.extension)
    save_imgs(args.output + "/glitched", glitched, args.extension)
    save_imgs(args.output + "/cropped", cropped, args.extension)
    save_imgs(args.output + "/glitched_tiled", glitched_tiled, args.extension)

        
    
    
