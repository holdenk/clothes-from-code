import re
from cowcowsecrets import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import http.cookiejar as cookielib
import random
import string
import mechanize

import time

cj = cookielib.LWPCookieJar()


target_album = "https://www.cowcow.com/Member/FileManager.aspx?folder=5788770&album=1"
file_manager = "https://www.cowcow.com/Member/FileManager.aspx"
login_url = "https://www.cowcow.com/Login.aspx?Return=%2fMember%2fFileManager.aspx"
bulk_product_url = "https://www.cowcow.com/Stores/StoreBulkProduct.aspx?StoreId=264507&SectionCode="

driver = webdriver.Firefox()

def construct_br():
    br = load_cookie_or_login()
    br.set_handle_robots(False)
    return br

def load_cookie_or_login():
    return do_login(username, password)

def do_login(username, password):
    """ Login to cowcow """
    driver.get(login_url)
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
    return None
    for img in imgs:
        print("Fetching file manager...")
        time.sleep(1)
        response = br.open(file_manager)
        # Manually specify the form
        br.form = mechanize.HTMLForm(
            'https://www.cowcow.com/AjaxUpload.ashx',
            method='POST', enctype='multipart/form-data')
        br.form.new_control('file', "files[]", {'id':'fileupload'})
        br.form.new_control('submit', 'Button', {})
        br.form.set_all_readonly(False)
        br.form.fixup()
        file_controller = br.find_control(id="fileupload", name="files[]")
        print("Adding img {0}".format(img))
        filename = re.sub("/", "_", img)
        file_controller.add_file(open(img, 'rb'), "image/png", filename)
        br.submit()


dress_filenames = [
    "front",
    "front_left",
    "front_right",
    "back_right",
    "sleeve_left",
    "pocket_right",
    "back_left",
    "back_rightside",
    "sleeve_right",
    "pocket_left",
    "back_leftside"]
def upload_dress_imgs(br, dress_output_directory):
    def create_absolute_filename(f):
        return "{0}/processed/{1}.png".format(
            dress_output_directory,
            f)
    imgs = map(create_absolute_filename, dress_filenames)
    return upload_imgs(imgs)

def create_dress(dress_output_directory):
    def filename_to_cowcow(f):
        return "{0}_processed_{1}.png({2})".format(
            dress_output_directory,
            f,
            re.sub("_", "", f))
    cowcow_img_specs = map(filename_to_cowcow, dress_filenames)
    cowcow_img_spec = " | ".join(cowcow_img_specs)
    cowcow_product_id = "2170"
    section_code = "01"
    unique_product_code = dress_output_directory + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    cowcow_product_spec = "{0}, {1}, {2}, {3}, {4}".format(
        cowcow_img_spec,
        cowcow_product_id,
        unique_product_code,
        section_code,
        "Glitch art dress for " + dress_output_directory)
    result = br.open(bulk_product_url)
    driver.get(bulk_product_url)
    print("Sending in {0}".format(cowcow_product_spec))
    textElem = driver.find_element_by_name("ctl00$cphMain$tbBulkAddProduct")
    textElem.clear()
    textElem.send_keys(cowcow_product_spec)
    updateElem = driver.find_element_by_id("ctl00_cphMain_ebImport")
#    updateElem = driver.find_element_by_name("import")
    updateElem.click()
    
    

dress_output_directory = "out"

br = construct_br()
upload_dress_imgs(br, dress_output_directory)
create_dress(dress_output_directory)
