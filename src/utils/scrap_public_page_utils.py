from datetime import datetime
from time import sleep
import locale

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from termcolor import colored


def scroll_down_to_reveal_posts(driver, public_page_id: str, amount_posts: int, since=None, until=None):
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
            break

    errors = []
    if since or until:
        filtered = []
        for link_date in post_links:
            link, date = link_date
            if date:
                if since and until:
                    if date >= since and date <= until:
                        filtered.append((link, date))
                elif since and until is None:
                    if date >= since:
                        filtered.append((link, date))
            else:
                errors.append(link)
        post_links = filtered

    return driver, post_links, errors


def clean_href(href: str) -> str:
    cleaned = href
    if "?" in href:
        cleaned = href.split("?")[0]
    return cleaned


def reveal_and_get_publication_date(driver, a_block):
    # This is to parse the names of the days and months in Spanish
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    # Hover mouse over to reveal publication date
    a = ActionChains(driver)
    a.move_to_element(a_block).perform()
    # Time necessary for the popup to be displayed
    sleep(3)
    specific_date_blocks = driver.find_elements(By.XPATH, "//div[@class='__fb-light-mode']")

    correct_amount_found = True
    is_a_date = True
    try:
        pub_date_text = specific_date_blocks[2].text
        pub_date = datetime.strptime(pub_date_text, "%A, %d de %B de %Y a las %H:%M")
    except IndexError:
        correct_amount_found = False
    except ValueError:
        is_a_date = False

    # If this isn't at least 3, then the popup did not displayed correctly
    # try once again but first scroll up the view a bit to fix it
    # also, check the text retrieved is actually a date
    while not(correct_amount_found) or not(is_a_date):
        print(colored("Warning: ", "red"), "Retrying to obtain specific publication date.")
        # Center block
        driver.execute_script("arguments[0].scrollIntoView();", a_block)
        a_block.send_keys(Keys.ESCAPE)
        a_block.send_keys(Keys.ARROW_DOWN)
        # Hover mouse over to reveal publication date
        a.move_to_element(a_block).perform()
        # Time necessary for the popup to be displayed
        sleep(3)
        specific_date_blocks = driver.find_elements(By.XPATH, "//div[@class='__fb-light-mode']")
        try:
            pub_date_text = specific_date_blocks[2].text
            correct_amount_found = True
            pub_date = datetime.strptime(pub_date_text, "%A, %d de %B de %Y a las %H:%M")
            is_a_date = True
        except IndexError:
            correct_amount_found = False
        except ValueError:
            is_a_date = False
            print(colored("Error: ", "red"), "Publication date could not be obtained.")
            return None

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
                hrefs.append((cleaned_link, pub_date))
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
