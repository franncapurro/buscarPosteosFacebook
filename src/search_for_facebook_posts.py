# -*- coding: utf-8 -*-

#    This file is part of buscarPostFacebook.
#
#    buscarPostFacebook is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    buscarPostFacebook is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with buscarPostFacebook; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
from itertools import zip_longest
from time import sleep

import click

from config_manager import ConfigManager
from utils.main_utils import (
    PostsSource,
    delete_duplicates,
    export_netvizz_csv,
    initialize_web_driver,
    login_to_facebook,
    remove_temp_files,
)
from utils.scrap_public_page_utils import (
    access_to_public_page,
    scroll_down_to_reveal_posts,
)
from utils.scrap_search_page_utils import get_post_links, search_for_word


def scrap_search_page(driver, config, search_term, amount, since, until):

    try:
        fb_search = search_for_word(driver, search_term)
        posts_links = get_post_links(fb_search, amount)
    except Exception as ex:
        print("ERROR" + str(ex))

    driver.quit()

    posts_links_to_scrap = delete_duplicates(posts_links)

    temp_filenames = export_netvizz_csv(config, posts_links_to_scrap)
    remove_temp_files(temp_filenames)


def scrap_public_page(driver, config, public_page, amount, since, until):
    driver = access_to_public_page(driver, public_page)
    # Time necessary for the page to be fully loaded
    sleep(5)
    driver, post_links = scroll_down_to_reveal_posts(driver, public_page, amount)
    posts_links_to_scrap = list(zip_longest(post_links, []))

    temp_filenames = export_netvizz_csv(config, posts_links_to_scrap)
    for temp_fn in temp_filenames:
        os.remove(temp_fn)


@click.command()
@click.option(
    "--source",
    type=click.Choice(
        [PostsSource.public_page.value, PostsSource.search_page.value],
    ),
    default=PostsSource.public_page.value,
    help="Source of the posts to be retrieved. For example: from a the search page or a specific public page, etc.",
)
@click.option("--word", prompt="Indicate a term to search or a public page ID")
@click.option("--amount", type=click.IntRange(min=1))
@click.option(
    "--since",
    type=click.DateTime(),
    help="Posts to be retrieved are those posted after the date given. Format is %Y-%m-%d",
)
@click.option(
    "--until",
    type=click.DateTime(),
    help="Posts to be retrieved are those posted before the date given. Format is %Y-%m-%d",
)
def main(source, word, amount, since, until):
    """
    Make use of the parameters the program received in order to execute the
    corresponding functions and, initialize the configuration and the web driver
    objects.
    """
    config = ConfigManager()
    driver = initialize_web_driver(config.gecko_binary)
    driver = login_to_facebook(driver, config.fb_username, config.fb_password)

    if source == PostsSource.search_page.value:
        scrap_search_page(driver, config, word, amount, since, until)
    elif source == PostsSource.public_page.value:
        scrap_public_page(driver, config, word, amount, since, until)


if __name__ == "__main__":
    main()
