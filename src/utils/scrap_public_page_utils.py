from datetime import datetime
from multiprocessing.sharedctypes import Value
from time import sleep
import locale
import platform

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from termcolor import colored


def scroll_down_to_reveal_posts(driver, public_page_id: str, amount_posts: int=None, since=None, until=None):
    body = driver.find_element_by_xpath("//body")
    post_links = []
    unknown = []
    # case in which it's requested to scrap publications after certain date 'since'
    if since:
        last_datetime_obtained = datetime.now()
        while last_datetime_obtained >= since:
            found_links, unknown_pub_date = reveal_post_links(driver, public_page_id)
            post_links.extend(found_links)
            unknown.extend(unknown_pub_date)
            last_datetime_obtained = post_links[-1][1]
            body.send_keys(Keys.CONTROL + Keys.END)
            # Time needed for the new posts to be fully loaded
            sleep(2)
            if amount_posts and len(post_links) >= amount_posts:
                post_links = post_links[:amount_posts]
                break
    elif since is None and amount_posts:
        # Assume 4 new posts per scrolldown, do at least 1
        amount_scrolls = amount_posts // 4 + 1
        for _ in range(0, amount_scrolls):
            found_links, unknown_pub_date = reveal_post_links(driver, public_page_id)
            post_links.extend(found_links)
            unknown.extend(unknown_pub_date)
            body.send_keys(Keys.CONTROL + Keys.END)
            # Time needed for the new posts to be fully loaded
            sleep(2)
            if len(post_links) >= amount_posts:
                post_links = post_links[:amount_posts]
                break

    return driver, post_links, unknown


def clean_href(href: str) -> str:
    cleaned = href
    if "?" in href:
        cleaned = href.split("?")[0]
    return cleaned


def find_publication_date(div_elements):
    for div in div_elements:
        pub_date_text = div.text
        try:
            pub_date = datetime.strptime(pub_date_text, "%A, %d de %B de %Y a las %H:%M")
            return pub_date
        except ValueError:
            continue
    return None


def reveal_and_get_publication_date(driver, a_block):
    # This is to parse the names of the days and months in Spanish
    if platform.system() != "Darwin":
        locale.setlocale(locale.LC_TIME, "es_AR")
    else:
        locale.setlocale(locale.LC_ALL, 'es_ES')
    # Hover mouse over to reveal publication date
    a = ActionChains(driver)
    a.move_to_element(a_block).perform()
    # Time necessary for the popup to be displayed
    sleep(3)
    specific_date_blocks = driver.find_elements(By.XPATH, "//div[@class='__fb-light-mode']")

    pub_date = find_publication_date(specific_date_blocks)
    if pub_date is None:
        a_block.send_keys(Keys.ARROW_DOWN)
        sleep(0.1)
        a_block.send_keys(Keys.ARROW_DOWN)
        sleep(0.1)
        a_block.send_keys(Keys.ARROW_DOWN)
        # Time necessary for the popup to be displayed
        sleep(3)
        specific_date_blocks = driver.find_elements(By.XPATH, "//div[@class='__fb-light-mode']")
        pub_date = find_publication_date(specific_date_blocks)
        if pub_date is None:
            print("Error:  Publication date could not be obtained.")

    # Reset locale to the default
    locale.setlocale(locale.LC_TIME, '')
    # Deselect anything
    a_block.send_keys(Keys.ESCAPE)
    
    return pub_date


def reveal_post_links(driver, public_page_id):
    # This a class name that's used to find specific URLs to the posts
    CLASS_NAME_FIND_LINK = "oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw"
    a_blocks = driver.find_elements(By.XPATH, f"//a[@class='{CLASS_NAME_FIND_LINK}']")
    url = build_public_page_url(public_page_id)
    hrefs = []
    unknown_pub_date = []
    for a_block in a_blocks:
        unreveald_link = a_block.get_attribute("href")
        if url in unreveald_link:
            if "#" in unreveald_link:
                if a_block.is_displayed():
                    a_block.click()
                    pub_date = reveal_and_get_publication_date(driver, a_block)
                    print(pub_date)
                revealed_link = a_block.get_attribute("href")
                cleaned_link = clean_href(revealed_link)
                if pub_date is None:
                    unknown_pub_date.append(cleaned_link)
                else:
                    hrefs.append((cleaned_link, pub_date))
                sleep(2)
    return hrefs, unknown_pub_date


def build_public_page_url(public_page_id: str) -> str:
    return f"https://www.facebook.com/{public_page_id}"


def access_to_public_page(
    driver: webdriver.Firefox, public_page_id: str
) -> webdriver.Firefox:
    url = build_public_page_url(public_page_id)
    driver.get(url)
    return driver
