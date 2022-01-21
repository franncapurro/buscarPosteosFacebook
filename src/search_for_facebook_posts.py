import os

from itertools import zip_longest
from time import sleep

from config_manager import ConfigManager
from utils.main_utils import delete_duplicates, remove_temp_files, initialize_web_driver, login_to_facebook, get_program_parameters, PostsSource
from utils.main_utils import export_netvizz_csv, delete_duplicates, remove_temp_files
from utils.scrap_public_page_utils import access_to_public_page, scroll_down_to_reveal_posts
from utils.scrap_search_page_utils import search_for_word, get_post_links

def scrap_search_page(driver, config):

    try:
        fb_search = search_for_word(driver, config.fb_page_name)
        posts_links = get_post_links(fb_search, config.amount_posts)
    except Exception as ex:
        print("ERROR" + str(ex))

    driver.quit()

    posts_links_to_scrap = delete_duplicates(posts_links)
    
    temp_filenames = export_netvizz_csv(config, posts_links_to_scrap)
    remove_temp_files(temp_filenames)


def scrap_public_page(driver, config, public_page, amount):
    driver = access_to_public_page(driver, public_page)
    # Time necessary for the page to be fully loaded
    sleep(5)
    driver, post_links = scroll_down_to_reveal_posts(driver, public_page, amount)
    posts_links_to_scrap = list(zip_longest(post_links, []))

    temp_filenames = export_netvizz_csv(config, posts_links_to_scrap)
    for temp_fn in temp_filenames:
        os.remove(temp_fn)


def main():
    """
    Make use of the parameters the program received in order to execute the
    corresponding functions and, initialize the configuration and the web driver
    objects. 
    """
    config = ConfigManager()
    driver = initialize_web_driver(config.gecko_binary)
    driver = login_to_facebook(driver, config.fb_username, config.fb_password)
    posts_source, public_page, amount = get_program_parameters()

    if posts_source == PostsSource.search_page.value:
        scrap_search_page(driver, config)
    elif posts_source == PostsSource.public_page.value:
        scrap_public_page(driver, config, public_page, amount)
    
if __name__ == "__main__":
    main()
