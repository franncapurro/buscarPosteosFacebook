import enum
import os
import sys
import traceback
from time import sleep
from typing import List, Tuple

import post_facebook
from config_manager import ConfigManager
from output_data_set_csv import OuputDataSetCSV
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.remote import webelement
from termcolor import colored
from webdriver_manager.firefox import GeckoDriverManager

FACEBOOK_LOGIN = "https://www.facebook.com/login/"
COLUMNS = [
    "type",
    "medio",
    "by",
    "post_id",
    "post_link",
    "post_message",
    "link",
    "post_published",
    "like_count_fb",
    "comments_count_fb",
    "reactions_count_fb",
    "shares_count_fb",
    "rea_LIKE",
    "rea_LOVE",
    "rea_WOW",
    "rea_HAHA",
    "rea_SAD",
    "rea_ANGRY",
    "rea_CARE",
]


class PostsSource(enum.Enum):
    public_page = "public_page"
    search_page = "search_page"


def delete_duplicates(posts_links):
    # this is because some links are repeated
    posts_links_to_scrap: List[Tuple[str, webelement.WebElement]] = []
    for url, html in posts_links:
        if url not in [p_l[0] for p_l in posts_links_to_scrap]:
            posts_links_to_scrap.append((url, html))
    return posts_links_to_scrap


def remove_temp_files(temp_filenames):
    for temp_fn in temp_filenames:
        os.remove(temp_fn)


def initialize_web_driver(firefox_path):
    """
    Parameters:
    - firefox_path: it's the path to the .exe file of Firefox in Windows.
    Returns:
    - the object to control a Firefox program instance.
    """
    f_options = Options()
    f_options.add_argument("--disable-notifications")
    f_options.binary_location = firefox_path

    f_prof = FirefoxProfile()
    f_prof.set_preference("dom.webnotifications.enabled", False)

    # Download the corresponding firefox driver
    exec_path = GeckoDriverManager().install()
    driver = webdriver.Firefox(service=Service(exec_path), options=f_options)

    return driver


def login_to_facebook(driver, username, password):

    driver.get(FACEBOOK_LOGIN)
    sleep(5)

    body = driver.find_element_by_xpath("//body")
    body.send_keys(username)
    body.send_keys(Keys.TAB)
    body.send_keys(password)
    body.send_keys(Keys.TAB)
    login_button = driver.find_element_by_css_selector("button[name='login']")
    login_button.send_keys(Keys.ENTER)
    print(colored("Logged into Facebook", "green"))
    sleep(15)

    return driver


def export_netvizz_csv(
    config: ConfigManager,
    posts_links: List[Tuple[str, webelement.WebElement]],
):

    posts_fb = OuputDataSetCSV(config.output_filename, COLUMNS)
    driver = initialize_web_driver(config.gecko_binary)
    fb_login = login_to_facebook(driver, config.fb_username, config.fb_password)

    temp_filenames = []
    for post_link_w_date, html_preview in posts_links:
        print(colored(f"Parsing post with url {post_link_w_date[0]}", "green"))
        try:
            post = post_facebook.PostFacebook(post_link_w_date[0], fb_login, html_preview)
            fn = post.save_html(config.base_path)
            posts = post.parse_post_html(publication_date=post_link_w_date[1])
            posts_fb.append(posts)
            temp_filenames.append(fn)
            sleep(10)
        except Exception as ex:
            print("ERROR" + str(ex) + traceback.format_exc())

    fb_login.quit()
    print(colored("Done!", "green"))
    posts_fb.save()
    return temp_filenames
