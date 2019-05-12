#!/usr/bin/env python
import random
from PIL import Image, ImageStat
import jpglitch
from pygments import highlight
from pygments.lexers import guess_lexer_for_filename
from pygments.formatters import JpgImageFormatter
from pygments.styles import get_all_styles
import io
import errno
import os
import math
import sys
from clothing import cowcow_items

# Some sketchy global configs
desired_max_tiles = 100
tile_target_width = 500
tile_target_height = 500
tile_variance_threshold = 500
tile_min_max_threshold = 110


def highlight_file(style, filename):
    """ Hightlight a given file guessing the lexer based on the extension """
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
            img_bytes = jpeg.new_bytes
        except IOError:
            break
    return Image.open(io.BytesIO(img_bytes))


def tileify(img):
    """
    Takes in an image and produces several smaller tiles.
    Tiles are uniform in shape but may not be uniformly cut.
    """

    def contains_interesting_code(img):
        """Returns true if the image tile contains enough variation"""
        stat = ImageStat.Stat(img)
        total_variance = sum(stat.var)
        min_max_diff = map(lambda x: x[1] - x[0], stat.extrema)
        min_max_diff_sum = sum(min_max_diff)
        print(
            "Got variance {0} from {1} min_max_dif {2} from {3}".format(
                total_variance, stat.var, min_max_diff_sum, min_max_diff
            )
        )
        return (
            total_variance > tile_variance_threshold
            and min_max_diff_sum > tile_min_max_threshold
        )

    offset_range = 50
    # crop takes (left, upper, right, lower)-tuple.
    source_size = img.size
    print("Source image size {0}".format(source_size))
    # Construct a list of possible areas of the input image
    # we want to turn into tiles
    candidate_coordinates = []
    # Generate tiles iteratively with some skew
    for w in range(int(math.ceil(source_size[0] / tile_target_width))):
        for h in range(int(math.ceil(source_size[1] / tile_target_height))):
            x_offset = min(
                source_size[0] - tile_target_width,
                (
                    random.randint(0, offset_range)
                    + source_size[0]
                    - ((w + 1) * tile_target_width)
                ),
            )
            y_offset = min(
                source_size[1] - tile_target_height,
                (
                    random.randint(0, offset_range)
                    + source_size[1]
                    - ((h + 1) * tile_target_height)
                ),
            )
            print(
                "Generating image for ({0},{1}) with offsets ({2},{3})".format(
                    w, h, x_offset, y_offset
                )
            )
            x0 = x_offset + (w * tile_target_width)
            y0 = y_offset + (h * tile_target_height)
            x1 = x_offset + ((w + 1) * tile_target_width)
            y1 = y_offset + ((h + 1) * tile_target_height)
            candidate_coordinates.append((x0, y0, x1, y1))
    # Generate 10 random tiles from "somewhere" in the image
    num_tiles_random = 10
    for _ in range(num_tiles_random):
        x0 = random.randint(0, source_size[0] - tile_target_width)
        y0 = random.randint(0, source_size[1] - tile_target_height)

        x1 = x0 + tile_target_width
        y1 = y0 + tile_target_height

        candidate_coordinates.append((x0, y0, x1, y1))
    # Take the coordinates and turn them into tile images, filtering out
    # antyhing which doesn't have any variation inside of it
    tiles = []
    for coordinates in candidate_coordinates:
        cropped_image = img.crop(coordinates)
        if contains_interesting_code(cropped_image):
            tiles.append(cropped_image)

    # If we have a lot of potential tiles generatinge everything is going to be slow
    num_tiles_to_return = min(desired_max_tiles, len(tiles))
    # Sampled without replacement yay
    return random.sample(tiles, num_tiles_to_return)


def build_tiles(filenames, style, amount_glitch, glitch_itr):
    """ Builds the tiles which we will assembly into a dress """
    # Highlight all of our inputs
    highlighted = map(lambda filename: highlight_file(style, filename), filenames)
    # Take the inputs and chop them up into tiles of a consistent size but semi random
    # locations
    ocropped = map(tileify, highlighted)
    print("cropped...")
    cropped = []
    for c in ocropped:
        for i in c:
            cropped.append(i)
    print("compacted to {0}".format(cropped))
    glitched_tiled = list(
        map(lambda img: glitch_image(img, amount_glitch, glitch_itr), cropped)
    )
    return (highlighted, cropped, glitched_tiled)


def build_image(
    filenames,
    style="paraiso-dark",
    amount_glitch=75,
    glitch_itr=6,
    percent_original=10,
    clothing="dress_with_pockets",
):
    (highlighted, cropped, glitched_tiled) = build_tiles(
        filenames, style, amount_glitch, glitch_itr
    )
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
        img = Image.new("RGB", dim)
        for i in range(0, dim[0], tile_target_width):
            for j in range(0, dim[1], tile_target_height):
                # Some tiles are bad, lets get another tile
                try:
                    img.paste(random_tile(), (i, j))
                except IOError:
                    img.paste(random_tile(), (i, j))
        return (name_dim[0], img)

    pieces = map(make_piece, cowcow_items[clothing].panels)

    return (pieces, highlighted, cropped, glitched_tiled)


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


def get_profiles():
    return cowcow_items.keys()


def list_profiles():
    print("The following clothing items are available:")
    for profile in get_profiles():
        print(profile)


def list_styles():
    print("The following styles are available:")
    for style in list(get_all_styles()):
        print(style)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process some code")
    parser.add_argument(
        "--files", type=str, default=["gen.py"], nargs="*", help="file names to process"
    )
    parser.add_argument(
        "--output", type=str, default="out", nargs="?", help="output directory"
    )
    parser.add_argument(
        "--extension", type=str, default="png", nargs="?", help="output extension"
    )
    parser.add_argument(
        "--clothing",
        type=str,
        default="dress_with_pockets",
        nargs="?",
        help="Clothing item to generate images for (see all available profiles with --list-clothing)",
    )
    parser.add_argument(
        "--list-clothing",
        dest="list_clothing",
        action="store_true",
        help="List all available clothing profiles and exit.",
    )
    parser.add_argument(
        "--style",
        type=str,
        default="paraiso-dark",
        nargs="?",
        help="The pygments style to use for the colour scheme (see all available styles with --list-styles)",
    )
    parser.add_argument(
        "--list-styles",
        dest="list_styles",
        action="store_true",
        help="List all available style names.",
    )

    args = parser.parse_args()

    if args.list_clothing:
        # The user just wants a list of profiles, let's print that and exit.
        list_profiles()

    if args.list_styles:
        # Again, the user just wants a list of styles, let's print that.
        list_styles()

    if args.list_styles or args.list_clothing:
        sys.exit(0)

    make_if_needed(args.output)
    print("Making the images in memory")
    (processed, highlighted, cropped, glitched_tiled) = build_image(
        args.files, clothing=args.clothing, style=args.style
    )
    print("Saving the images to disk")
    save_imgs(args.output + "/processed", processed, args.extension)
    save_imgs(args.output + "/highlighted", highlighted, args.extension)
    save_imgs(args.output + "/cropped", cropped, args.extension)

    save_imgs(args.output + "/glitched_tiled", glitched_tiled, args.extension)
