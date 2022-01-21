from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def scroll_down_to_reveal_posts(driver, public_page_id: str, amount_posts: int):
    # Assume 4 new posts per scrolldown, do at least 1
    amount_scrolls = amount_posts // 4 + 1
    body = driver.find_element_by_xpath("//body")
    post_links = []
    for _ in range(0, amount_scrolls):
        found_links = reveal_post_links(driver, public_page_id)
        post_links.extend(found_links)
        body.send_keys(Keys.CONTROL + Keys.END)
        # Time needed for the new posts to be fully loaded
        sleep(2)
        if len(post_links) >= amount_posts:
            post_links = post_links[:amount_posts]
            return driver, post_links
    return driver, post_links


def clean_href(href: str) -> str:
    cleaned = href
    if "?" in href:
        cleaned = href.split("?")[0]
    return cleaned


def reveal_post_links(driver, public_page_id):
    # This a class name that's used to find specific URLs to the posts
    CLASS_NAME_FIND_LINK = "oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw"
    a_blocks = driver.find_elements(By.XPATH, f"//a[@class='{CLASS_NAME_FIND_LINK}']")
    url = build_public_page_url(public_page_id)
    hrefs = []
    for a_block in a_blocks:
        unreveald_link = a_block.get_attribute("href")
        if url in unreveald_link:
            if "#" in unreveald_link:
                if a_block.is_displayed():
                    a_block.click()
                revealed_link = a_block.get_attribute("href")
                cleaned_link = clean_href(revealed_link)
                hrefs.append(cleaned_link)
                sleep(2)
    return hrefs


def build_public_page_url(public_page_id: str) -> str:
    return f"https://www.facebook.com/{public_page_id}"


def access_to_public_page(
    driver: webdriver.Firefox, public_page_id: str
) -> webdriver.Firefox:
    url = build_public_page_url(public_page_id)
    driver.get(url)
    return driver
