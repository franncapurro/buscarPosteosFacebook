import os
import platform
from datetime import datetime
from time import sleep
import traceback

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from termcolor import colored
from webdriver_manager.firefox import GeckoDriverManager

import ConfigManager
import PostFacebook
from OutputDataSetCSV import OuputDataSetCSV


def getFBLogin(fb_user, fb_password, gecko_binary, gecko_driver_exe, headless=False):
    driver = getFBPage('https://www.facebook.com/login/', gecko_binary, gecko_driver_exe, headless)
    body = driver.find_element_by_xpath('//body')
    body.send_keys(fb_user)
    body.send_keys(Keys.TAB)
    body.send_keys(fb_password)
    body.send_keys(Keys.TAB)
    loginbutton = driver.find_element_by_css_selector("button[name='login']")
    loginbutton.send_keys(Keys.ENTER)
    print(colored('Logged into Facebook', 'green'))
    sleep(15)
    return driver


def getFBPage(url, gecko_binary, gecko_driver_exe, headless=False):
    ffoptions = Options()
    ffoptions.add_argument("--disable-notifications")
    if headless:
        ffoptions.headless = True

    ffprofile = FirefoxProfile()
    ffprofile.set_preference("dom.webnotifications.enabled", False)

    if platform.system() == 'Windows':
        ffoptions.binary_location = gecko_binary
        # Download the corresponding firefox driver
        executable_path = GeckoDriverManager().install()
        s = Service(executable_path)
        driver = webdriver.Firefox(service=s, options=ffoptions)
    else:
        driver = webdriver.Firefox(options=ffoptions, firefox_profile=ffprofile)

    driver.get(url)
    sleep(5)
    return driver


def getFBSearchPage(driver, page, year):
    search_textbox = driver.find_element_by_css_selector("input[type='search'][aria-label]")
    search_textbox.send_keys(page.encode("utf_8").decode("utf_8"))
    search_textbox.send_keys(Keys.ENTER)
    sleep(15)
    #body = driver.find_element_by_xpath('//body')
    #body.send_keys(Keys.TAB)
    #body.send_keys(Keys.TAB)
    #body.send_keys(Keys.TAB)
    #body.send_keys(Keys.ENTER)
    #sleep(5)
    
    #body = driver.find_element_by_xpath('//body')
    #body.send_keys(Keys.TAB)
    #body.send_keys(Keys.TAB)
    #body.send_keys(Keys.TAB)
    #body.send_keys(Keys.TAB)
    #body.send_keys(Keys.TAB)
    #body.send_keys(Keys.ENTER)
    #sleep(5)
    
    # tantos para abajo como años
    #year_count = datetime.now().year - int(year)
    #for _ in range(0, year_count):
    #    body.send_keys(Keys.ARRgit OW_DOWN)
    #body.send_keys(Keys.ENTER)

    #sleep(2)

    #search_textbox = driver.find_element_by_css_selector("input[type='search'][aria-label]")
    #search_textbox.send_keys(Keys.TAB)
    #for _ in range(0, 17):
    #    elem = driver.switch_to_active_element()
    #    elem.send_keys(Keys.TAB)
    #    sleep(1)

    #sleep(20)
    #elem = driver.switch_to_active_element()
    #elem.send_keys(' ' + page)

    sleep(2)
    elem = driver.switch_to.active_element
    elem.send_keys(Keys.ARROW_DOWN)

    search_textbox = driver.find_elements_by_css_selector("li.k4urcfbm[role='option']")
    for elem in search_textbox:
        if elem.text.upper() == page.upper():
            elem.click()
            break

    return driver


def getFBPostsLinks(driver, amount_of_publications):
    AMOUNT_OF_SCROLLS = 5
    scroll_nro = 0
    while HasScroll(driver) and scroll_nro < AMOUNT_OF_SCROLLS:
        body = driver.find_element_by_xpath('//body')
        body.send_keys(Keys.CONTROL + Keys.END)
        scroll_nro = scroll_nro + 1
        sleep(3)
    sleep(5)
    body = driver.find_element_by_xpath('//body')
    posts = body.find_elements_by_class_name('sjgh65i0')
    posts_links_html = []
    for post in posts:
        specific_span_tags = post.find_elements_by_xpath("//span[contains(@id, 'jsc_c')]")
        for sst in specific_span_tags:
            if len(posts_links_html) >= amount_of_publications:
                break
            if "·" in sst.text:
                a_tags = sst.find_elements_by_tag_name("a")
                for a_tag in a_tags:
                    if len(posts_links_html) >= amount_of_publications:
                        break
                    if a_tag.get_attribute("role")=="link":
                        # sometimes the obtained href value obtained might not be the specific link to the FB pub
                        # in those case, it'll change to the correct link once a click is executed over it
                        if "search" in a_tag.get_attribute("href"):
                            sleep(1)
                            a_tag.click()
                        href = a_tag.get_attribute("href")
                        inner_html = post.get_attribute("innerHTML")
                        if href not  in [post_data[0] for post_data in posts_links_html]:
                            # avoid duplicates
                            print(colored(f"Post obtained: {href}", "green"))
                            posts_links_html.append((href, inner_html))
    print(colored(f"Posts to scrap: {len([post_data[0] for post_data in posts_links_html])}", "green"))
    return posts_links_html


def HasScroll(driver):
    return driver.find_element_by_tag_name('div')


def exportLinksCsv(config, posts_links):
    columns = ['post_link']
    now = datetime.now()
    date_time = now.strftime("%m_%d_%Y_%H_%M_%S")
    filename_csv = config.output_post_filename_prefix + str(date_time) + ".csv"
    output_filename_csv = os.path.join(config.base_path, filename_csv)
                                       
    posts_fb = OuputDataSetCSV(output_filename_csv, columns)
    for post_link in posts_links:
        posts_fb.append([post_link[0]])
    posts_fb.save()


def exportNetvizzCsv(config, posts_links):
    columns = ['type', 'medio', 'by', 'post_id', 'post_link', 'post_message', 'picture', 'full_picture', 'link', 'link_domain', 'post_published', 'post_published_unix', 'post_published_sql', 'post_hora_argentina', 'like_count_fb', 'comments_count_fb', 'reactions_count_fb', 'shares_count_fb', 'engagement_fb', 'rea_LIKE', 'rea_LOVE', 'rea_WOW', 'rea_HAHA', 'rea_SAD', 'rea_ANGRY', 'post_picture_descripcion', 'poll_count', 'titulo_link', 'subtitulo_link', 'menciones', 'hashtags', 'video_plays_count', 'fb_action_tags_text', 'has_emoji', 'tiene_hashtags', 'tiene_menciones']
    posts_fb = OuputDataSetCSV(config.output_filename, columns)

    fb_login = getFBLogin(config.fb_username, config.fb_password, config.gecko_binary, config.gecko_driver_exe, config.gecko_headless)
    for post_link, html_preview in posts_links:
        print(colored(f"Parsing post with url {post_link}", "green"))
        try:
            post = PostFacebook.PostFacebook(post_link, fb_login, html_preview)
            post.SaveHtml(config.base_path)
            posts = post.ParsePostHTML()
            posts_fb.append(posts)
            sleep(10)
        except Exception as ex:
            print("ERROR" + str(ex) + traceback.format_exc()) 
    
    fb_login.quit()
    print(colored("Done!", "green"))
    posts_fb.save()


# Programa Principal
config = ConfigManager.ConfigManager()

driver = getFBLogin(config.fb_username, config.fb_password, config.gecko_binary, config.gecko_driver_exe, config.gecko_headless)
posts_links = []

try:
    fb_search = getFBSearchPage(driver, config.fb_page_name,
                                config.fb_search_year)
    posts_links = getFBPostsLinks(fb_search, config.max_scroll)
except Exception as ex:
    print("ERROR" + str(ex))

# this is because some links are repeated
posts_links_to_scrap = []
for url, html in posts_links:
    if url not in [p_l[0] for p_l in posts_links_to_scrap]:
        posts_links_to_scrap.append((url, html))

exportLinksCsv(config, posts_links_to_scrap)
driver.quit()

exportNetvizzCsv(config, posts_links_to_scrap)