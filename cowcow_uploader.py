import argparse
import re
from cowcowsecrets import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import http.cookiejar as cookielib
import random
import string
import mechanize
from clothing import cowcow_items

import time

cj = cookielib.LWPCookieJar()


target_album = "https://www.cowcow.com/Member/FileManager.aspx?folder=5788770&album=1"
file_manager = "https://www.cowcow.com/Member/FileManager.aspx"
login_url = "https://www.cowcow.com/Login.aspx?Return=%2fMember%2fFileManager.aspx"
bulk_product_url = "https://www.cowcow.com/Stores/StoreBulkProduct.aspx?StoreId=264507&SectionCode="


def construct_br(driver):
    br = load_cookie_or_login(driver)
    br.set_handle_robots(False)
    return br


def load_cookie_or_login(driver):
    # Todo: cache cookies
    return do_login(driver, username, password)


def do_login(driver, username, password):
    """ Login to cowcow """
    print("Logging into cowcow to upload")
    driver.get(login_url)
    # Give firefox a few cycles to find the driver title
    c = 0
    while "Login" not in driver.title and c < 10:
        print("Driver title is: {0}".format(driver.title))
        time.sleep(1)
        c = c+1
    assert "Login" in driver.title
    username_elem = driver.find_element_by_name("tbEmail")
    username_elem.clear()
    username_elem.send_keys(username)
    password_elem = driver.find_element_by_name("tbPassword")
    password_elem.clear()
    password_elem.send_keys(password)
    password_elem.send_keys(Keys.RETURN)
    time.sleep(5)
    assert "Login" not in driver.title
    # Grab the cookie
    cookie = driver.get_cookies()

    # Store it in the cookie jar
    cj = cookielib.LWPCookieJar()

    for s_cookie in cookie:
        cj.set_cookie(cookielib.Cookie(
            version=0,
            name=s_cookie['name'],
            value=s_cookie['value'],
            port='80', port_specified=False, domain=s_cookie['domain'],
            domain_specified=True, domain_initial_dot=False, path=s_cookie['path'],
            path_specified=True, secure=s_cookie['secure'], expires=None,
            discard=False, comment=None, comment_url=None, rest=None, rfc2109=False))

    # cj.save("cookies.txt") -- this fails idk why
    # Instantiate a Browser and set the cookies
    br = mechanize.Browser()
    br.set_cookiejar(cj)
    return br


def upload_imgs(imgs):
    """ Upload the images to cowcow """
    print("Uploading...")
    for img in imgs:
        print("Fetching file manager...")
        time.sleep(2)
        response = br.open(file_manager)
        # Manually specify the form
        br.form = mechanize.HTMLForm(
            'https://www.cowcow.com/AjaxUpload.ashx',
            method='POST', enctype='multipart/form-data')
        br.form.new_control('file', "files[]", {'id': 'fileupload'})
        br.form.new_control('submit', 'Button', {})
        br.form.set_all_readonly(False)
        br.form.fixup()
        file_controller = br.find_control(id="fileupload", name="files[]")
        print("Adding img {0}".format(img))
        filename = re.sub("/", "_", img)
        with open(img, 'rb') as img_handle:
            try:
                print("Opened img {0}".format(img))
                file_controller.add_file(img_handle, "image/png", filename)
                print("Added img to controller")
                br.submit()
                print("Submitted form".format(img))
            except Error as e:
                print("Sad :(")
                print("Error {0} adding img {1}".format(e, img))
                raise


def upload_dress_imgs(br, clothing_name, dress_output_directory):
    def create_absolute_filename(f):
        return "{0}/processed/{1}.png".format(
            dress_output_directory,
            f)
    dress_filenames = map(lambda x: x[0], cowcow_items[clothing_name].panels)
    imgs = map(create_absolute_filename, dress_filenames)
    print("Uploading the images.")
    return upload_imgs(imgs)


def create_dress(driver, clothing_name, dress_output_directory, dress_name):
    def filename_to_cowcow(f):
        cowcowname = "{0}_processed_{1}.png({2})".format(
            dress_output_directory,
            f,
            # Our filenames are the names of the cowcow pieces but with _s, so strip them
            re.sub("_", "", f)
        )
        # Any /s are replaced with _s so we play nice with the file manager
        cowcowname = re.sub("/", "_", cowcowname)
        return cowcowname

    dress_filenames = map(lambda x: x[0], cowcow_items[clothing_name].panels)
    cowcow_img_specs = map(filename_to_cowcow, dress_filenames)
    cowcow_img_spec = " | ".join(cowcow_img_specs)
    cowcow_product_id = cowcow_items[clothing_name].cowcowid
    section_code = "01"
    unique_product_code = dress_output_directory + \
        ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    cowcow_product_spec = "{0}, {1}, {2}, {3}, {4}".format(
        cowcow_img_spec,
        cowcow_product_id,
        unique_product_code,
        section_code,
        dress_name)
    def configure_product():
        result = br.open(bulk_product_url)
        print("Creating the product entry")
        driver.get(bulk_product_url)
        print("Sending in {0}".format(cowcow_product_spec))
        textElem = driver.find_element_by_name("ctl00$cphMain$tbBulkAddProduct")
        textElem.clear()
        textElem.send_keys(cowcow_product_spec)
        updateElem = driver.find_element_by_id("ctl00_cphMain_ebImport")
        updateElem.click()
        # Kind of a hack, but the image should upload within 10
        time.sleep(10)
    configure_product()


if __name__ == "__main__":
    print("Hi! I'm your friendly cowcow uploader. I am slow. Please waite.")
    parser = argparse.ArgumentParser(description='Upload a dress to cowcow')
    parser.add_argument('--dress_name', type=str,
                        nargs="?",
                        help="name of the dress")
    parser.add_argument('--dress_dir', type=str,
                        nargs="?",
                        help="directory where the dress files all live")
    parser.add_argument(
        "--clothing",
        type=str,
        default="dress_with_pockets",
        nargs="?",
        help="Clothing item to generate images for (see all available profiles with --list-clothing)",
        )
    parser.add_argument('--foreground-gecko',
                        dest="foreground_gecko",
                        action="store_true",
                        help="run the driver in the foreground for debugging")
    args = parser.parse_args()
    print("Args parsed.")
    try:
        options = webdriver.ChromeOptions()

        if not args.foreground_gecko:
            options.headless = True
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")

        print("Launching driver....")
        driver = webdriver.Chrome(options=options)

        br = construct_br(driver)
        print("Uploading the dress....")
        upload_dress_imgs(br, args.clothing, args.dress_dir)
        print("Creating the dress....")
        create_dress(driver, args.clothing, args.dress_dir, args.dress_name)
        print("Finished talking to cowcow...")
    finally:
        print("Cleaning up the driver")
        driver.close()
