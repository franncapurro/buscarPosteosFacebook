import os
import platform
import traceback
from datetime import datetime
from time import sleep
from typing import List, Tuple

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.remote import webelement
from termcolor import colored
from webdriver_manager.firefox import GeckoDriverManager

import ConfigManager
import post_facebook
from output_data_set_csv import OuputDataSetCSV


def get_fb_login(
    fb_user: str, fb_password: str, gecko_binary, headless: bool = False
) -> webdriver.Firefox:
    fb_login = "https://www.facebook.com/login/"
    driver = get_fb_page(fb_login, gecko_binary, headless)
    body = driver.find_element_by_xpath("//body")
    body.send_keys(fb_user)
    body.send_keys(Keys.TAB)
    body.send_keys(fb_password)
    body.send_keys(Keys.TAB)
    login_button = driver.find_element_by_css_selector("button[name='login']")
    login_button.send_keys(Keys.ENTER)
    print(colored("Logged into Facebook", "green"))
    sleep(15)
    return driver


def get_fb_page(url: str, gecko, headless: bool = False) -> webdriver.Firefox:
    f_options = Options()
    f_options.add_argument("--disable-notifications")
    if headless:
        f_options.headless = True

    f_prof = FirefoxProfile()
    f_prof.set_preference("dom.webnotifications.enabled", False)

    if platform.system() == "Windows":
        f_options.binary_location = gecko
        # Download the corresponding firefox driver
        executable_path = GeckoDriverManager().install()
        s = Service(executable_path)
        driver = webdriver.Firefox(service=s, options=f_options)
    else:
        driver = webdriver.Firefox(options=f_options, firefox_profile=f_prof)

    driver.get(url)
    sleep(5)
    return driver


def get_search(driver: webdriver.Firefox, page: str) -> webdriver.Firefox:
    sleep(2)
    css_slector = "input[type='search'][aria-label]"
    search = driver.find_element_by_css_selector(css_slector)
    search.send_keys(page.encode("utf_8").decode("utf_8"))
    search.send_keys(Keys.ENTER)
    sleep(15)
    sleep(2)
    elem = driver.switch_to.active_element
    elem.send_keys(Keys.ARROW_DOWN)

    css_selector = "li.k4urcfbm[role='option']"
    search = driver.find_elements_by_css_selector(css_selector)
    for elem in search:
        if elem.text.upper() == page.upper():
            elem.click()
            break

    return driver


def get_fb_post_linnks(
    driver: webdriver.Firefox, amount_of_publications: int
) -> List[Tuple[str, webelement.WebElement]]:
    AMOUNT_OF_SCROLLS = 5
    scroll_nro = 0
    while has_scroll(driver) and scroll_nro < AMOUNT_OF_SCROLLS:
        body = driver.find_element_by_xpath("//body")
        body.send_keys(Keys.CONTROL + Keys.END)
        scroll_nro = scroll_nro + 1
        sleep(3)
    sleep(5)
    body = driver.find_element_by_xpath("//body")
    posts = body.find_elements_by_class_name("sjgh65i0")
    posts_links_html: List[Tuple[str, webelement.WebElement]] = []
    for post in posts:
        specific_span_tags = post.find_elements_by_xpath(
            "//span[contains(@id, 'jsc_c')]"
        )
        for sst in specific_span_tags:
            if len(posts_links_html) >= amount_of_publications:
                break
            if "·" in sst.text:
                a_tags = sst.find_elements_by_tag_name("a")
                for a_tag in a_tags:
                    if len(posts_links_html) >= amount_of_publications:
                        break
                    if a_tag.get_attribute("role") == "link":
                        # sometimes the obtained href value obtained might not
                        # be the specific link to the FB pub in those case,
                        # it'll change to the correct link once a click is
                        # executed over it
                        if "search" in a_tag.get_attribute("href"):
                            sleep(1)
                            a_tag.click()
                        href = a_tag.get_attribute("href")
                        inner_html = post.get_attribute("innerHTML")
                        hrefs = [p_l[0] for p_l in posts_links_html]
                        if href not in hrefs:
                            # avoid duplicates
                            print(colored(f"Post obtained: {href}", "green"))
                            posts_links_html.append((href, inner_html))
    hrefs = [post_data[0] for post_data in posts_links_html]
    print(
        colored(
            f"Posts to scrap: {len(hrefs)}",
            "green",
        )
    )
    return posts_links_html


def has_scroll(driver: webdriver.Firefox) -> webelement.WebElement:
    return driver.find_element_by_tag_name("div")


def export_links_csv(
    config: ConfigManager.ConfigManager,
    posts_links: List[Tuple[str, webelement.WebElement]],
):
    """
    Save a table containing the links to the FB posts.
    """
    columns = ["post_link"]
    now = datetime.now()
    date_time = now.strftime("%m_%d_%Y_%H_%M_%S")
    filename_csv = config.output_post_filename_prefix + str(date_time) + ".csv"
    output_filename_csv = os.path.join(config.base_path, filename_csv)

    posts_fb = OuputDataSetCSV(output_filename_csv, columns)
    for post_link in posts_links:
        posts_fb.append([post_link[0]])
    posts_fb.save()


def export_netvizz_csv(
    config: ConfigManager.ConfigManager,
    posts_links: List[Tuple[str, webelement.WebElement]],
):
    columns = [
        "type",
        "medio",
        "by",
        "post_id",
        "post_link",
        "post_message",
        # 'picture',
        # 'full_picture',
        "link",
        # 'link_domain',
        "post_published",
        # 'post_published_unix',
        # 'post_published_sql',
        # 'post_hora_argentina',
        "like_count_fb",
        "comments_count_fb",
        "reactions_count_fb",
        "shares_count_fb",
        # 'engagement_fb',
        "rea_LIKE",
        "rea_LOVE",
        "rea_WOW",
        "rea_HAHA",
        "rea_SAD",
        "rea_ANGRY",
        # 'post_picture_descripcion',
        # 'poll_count',
        # 'titulo_link',
        # 'subtitulo_link',
        # 'menciones',
        # 'hashtags',
        # 'video_plays_count',
        # 'fb_action_tags_text',
        # 'has_emoji',
        # 'tiene_hashtags',
        # 'tiene_menciones'
    ]
    posts_fb = OuputDataSetCSV(config.output_filename, columns)

    fb_login = get_fb_login(
        config.fb_username,
        config.fb_password,
        config.gecko_binary,
        config.gecko_headless,
    )
    temp_filenames = []
    for post_link, html_preview in posts_links:
        print(colored(f"Parsing post with url {post_link}", "green"))
        try:
            post = post_facebook.PostFacebook(post_link, fb_login, html_preview)
            fn = post.SaveHtml(config.base_path)
            posts = post.ParsePostHTML()
            posts_fb.append(posts)
            temp_filenames.append(fn)
            sleep(10)
        except Exception as ex:
            print("ERROR" + str(ex) + traceback.format_exc())

    fb_login.quit()
    print(colored("Done!", "green"))
    posts_fb.save()
    return temp_filenames


# Programa Principal
conf = ConfigManager.ConfigManager()

driver = get_fb_login(
    conf.fb_username, conf.fb_password, conf.gecko_binary, conf.gecko_headless
)
posts_links = []

try:
    fb_search = get_search(driver, conf.fb_page_name)
    posts_links = get_fb_post_linnks(fb_search, conf.amount_posts)
except Exception as ex:
    print("ERROR" + str(ex))

# this is because some links are repeated
posts_links_to_scrap: List[Tuple[str, webelement.WebElement]] = []
for url, html in posts_links:
    if url not in [p_l[0] for p_l in posts_links_to_scrap]:
        posts_links_to_scrap.append((url, html))

# export_links_csv(conf, posts_links_to_scrap)
driver.quit()

temp_filenames = export_netvizz_csv(conf, posts_links_to_scrap)
for temp_fn in temp_filenames:
    os.remove(temp_fn)

