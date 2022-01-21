from time import sleep
from typing import List, Tuple

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote import webelement
from termcolor import colored


def has_scroll(driver: webdriver.Firefox) -> webelement.WebElement:
    return driver.find_element_by_tag_name("div")


def search_for_word(driver: webdriver.Firefox, page: str) -> webdriver.Firefox:
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


def get_post_links(
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
