import hashlib
import locale
import os
import platform
import urllib.request
from datetime import datetime, timedelta
from time import sleep
from urllib.request import urlretrieve

import bs4
from PIL import Image
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        ElementNotInteractableException,
                                        NoSuchElementException)
from selenium.webdriver.common.keys import Keys
from termcolor import colored

from facebook_string_to_number import FacebookStringToNumber
from text_output_file import TextOutputFile


class PostFacebook:
    def __init__(self, urlLink, fb_login, html_preview):
        self.urlLink = urlLink
        self.fb_login = fb_login
        # HTML obtained from search page
        self.html_preview = html_preview
        self.html_preview_bs = self._get_html_post(html_preview)
        # HTML obtained from the publication specific link
        self.html_raw = self._get_html_facebook()
        self.html_bs = self._get_html_post(self.html_raw)

        self.fbStringToNumber = FacebookStringToNumber()

    def _get_html_facebook(self):
        url = self.urlLink.replace("videos", "posts")
        self.fb_login.get(url)
        sleep(5)

        body = self.fb_login.find_element_by_xpath("//body")
        body.send_keys(Keys.ESCAPE)
        sleep(1)
        html = None
        try:
            post = self.fb_login.find_element_by_css_selector(".du4w35lb.l9j0dhe7")
            html = post.get_attribute("innerHTML")
        except Exception as ex:
            print(colored("ERROR" + str(ex), "red"))
        return html

    def _get_html_post(self, html_raw):
        contenido = None
        if html_raw:
            contenido = bs4.BeautifulSoup(html_raw, "lxml")
        return contenido

    def save_html(self, base_path):
        post_id, page_id = self.get_post_id()
        text_output_file = TextOutputFile(str(self.html_raw))
        text_output_filename = "post_page_" + page_id + "_" + post_id + ".html"
        output_filename_html = os.path.join(base_path, text_output_filename)
        # use a hash to create a unique simpler filename
        hash_object = hashlib.md5(output_filename_html.encode())
        text_output_file.save(f"file_{hash_object.hexdigest()}")
        return f"file_{hash_object.hexdigest()}"

    def parse_post_html(self, publication_date):
        posts = []

        page_name = self.get_page_name()
        if page_name is None:
            print(colored("ERROR: page name could not be obtained", "red"))
            return posts
        # type
        posts.append("")
        # medio
        posts.append(page_name)

        post_id, page_id = self.get_post_id()
        # by
        posts.append(page_id)
        # post_id
        posts.append(post_id)
        post_url = self.get_post_url(page_id, post_id)
        # post_link
        posts.append(post_url)

        post_message = self.get_post_message()
        # post_message
        posts.append(post_message)

        link = ""
        link_div = self.html_bs.find_all(
            "a",
            {
                "class": "oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 datstx6m k4urcfbm"
            },
        )
        if link_div:
            a_link_tag = link_div[0]
            a_link_href = a_link_tag.get("href")
            a_link_url_query = urllib.parse.urlsplit(a_link_href).query
            link_dict = urllib.parse.parse_qs(a_link_url_query)
            link = link_dict.get("u", [""])[0]
            posts[0] = "link"
        else:
            link_video = self.html_bs.select("video[src]")
            if link_video:
                a_link_href = self.get_video_link(link_video)
                posts[0] = "video"
            else:
                link_imagen_tag = self.html_bs.find_all(
                    "a", {"class": "_4-eo _2t9n _50z9"}
                )
                if link_imagen_tag:
                    a_link_href = link_imagen_tag[0].get("href")
                    link = "https://www.facebook.com" + a_link_href
                    posts[0] = "imagen"
                else:
                    link_imagen_tag = self.html_bs.find_all(
                        "a", {"class": "_6k_ _4-eo _5dec _1ktf"}
                    )
                    if link_imagen_tag:
                        a_link_href = link_imagen_tag[0].get("href")
                        link = "https://www.facebook.com" + a_link_href
                        posts[0] = "imagen"
                    else:
                        link_imagen_tag = self.html_bs.find_all(
                            "a", {"class": "_4-eo _2t9n"}
                        )
                        if link_imagen_tag:
                            a_link_href = link_imagen_tag[0].get("href")
                            link = "https://www.facebook.com" + a_link_href
                            posts[0] = "imagen"
                        else:
                            cabecera_span_tag = self.html_bs.find_all(
                                "span", {"class": "fcg"}
                            )
                            for span in cabecera_span_tag:
                                if "encuesta" in str(span):
                                    posts[0] = "encuesta"
                                    break
        # link
        posts.append(link)
        # posts.append(link_domain)

        if publication_date is None:
            # post_published
            (
                post_published_str,
                post_published_unix,
                post_published_sql,
                post_date_argentina,
            ) = self.get_post_date()
            # post_published
            posts.append(post_published_str)
        else:
            post_date = publication_date.strftime("%d/%m/%Y %H:%M:%S")
            posts.append(post_date)

        (
            like_count_fb,
            rea_LOVE,
            rea_WOW,
            rea_HAHA,
            rea_SAD,
            rea_ANGRY,
            rea_CARE,
        ) = self.get_reactions()
        # like_count_fb
        posts.append(like_count_fb)

        # comments_count_fb
        comments_count = self.get_comments_count(self.fbStringToNumber)
        # comments_count_fb
        posts.append(comments_count)

        reactions_count = self.get_reactions_count(self.fbStringToNumber)
        # reactions_count_fb
        posts.append(reactions_count)

        shares_count = self.get_shares_count(self.fbStringToNumber)
        # shares_count_fb
        posts.append(shares_count)

        # try:
        #     engagement_fb = comments_count + reactions_count + shares_count
        #   # engagement_fb
        #     posts.append(engagement_fb)
        # except Exception:
        #     posts.append('')

        # rea_LIKE
        posts.append(like_count_fb)
        # rea_LOVE
        posts.append(rea_LOVE)
        # rea_WOW
        posts.append(rea_WOW)
        # rea_HAHA
        posts.append(rea_HAHA)
        # rea_SAD
        posts.append(rea_SAD)
        # rea_ANGRY
        posts.append(rea_ANGRY)
        # rea_CARE
        posts.append(rea_CARE)

        return posts

    def get_post_date(self):
        """
        The date may be shown in any of the following ways:
        3 de diciembre de 2021
        14 de diciembre de 2021 a las 15:30
        2 días
        1 min
        8 h
        Hace un momento
        """
        if platform.system() != "Darwin":
            locale.setlocale(locale.LC_TIME, "es_AR")
        else:
            locale.setlocale(locale.LC_ALL, 'es_ES')
        a_date = self.html_bs.find_all(
            "a",
            {
                "class": "oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw"
            },
        )
        if a_date:
            a_date_text = a_date[0].get("aria-label")
            tokens = a_date_text.split(" ")
            if len(tokens) == 2 and "h" in tokens:
                # 8 h
                hours = int(a_date_text.replace("h", "").strip())
                post_date = datetime.now() - timedelta(hours=hours)
            elif len(tokens) == 2 and "min" in tokens:
                # 1 min
                minutes = int(a_date_text.replace("min", "").strip())
                post_date = datetime.now() - timedelta(minutes=minutes)
            elif len(tokens) == 2 and "d" in a_date_text:
                # 2 días
                a_date_text = a_date_text.replace(" ", "").replace("d", "")
                days = int(a_date_text.replace("d", "").strip())
                post_date = datetime.now() - timedelta(hours=24 * days)
            elif len(tokens) == 8 and "las" in tokens:
                # 14 de diciembre de 2021 a las 15:30
                day, month, year = tokens[0], tokens[2], tokens[4]
                text_in_new_format = f"{day} {month} {year}"
                post_date = datetime.strptime(text_in_new_format, "%d %B %Y")
            elif len(tokens) == 2 and "momento" in tokens:
                # Hace un momento
                post_date = datetime.now()
            elif len(tokens) == 5 and "de" in [tokens[1], tokens[3]]:
                # 3 de diciembre de 2021
                day, month, year = tokens[0], tokens[2], tokens[4]
                text_in_new_format = f"{day} {month} {year}"
                post_date = datetime.strptime(text_in_new_format, "%d %B %Y")
            else:
                print(colored("ERROR: publication date could not be parsed", "red"))
                return ("", float(0), None, None)

            post_published_str = post_date.strftime("%Y-%m-%d %H:%M:%S")
            post_published_unix = float(0)
            post_published_sql = None
            post_date_argentina = None

        return (
            post_published_str,
            post_published_unix,
            post_published_sql,
            post_date_argentina,
        )

    def get_video_link(self, link_video):
        link = link_video[0].get("src")
        if link:
            link = link.replace("blob:", "")
        return link

    def get_page_name(self):
        CLASS_NAME = "oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gpro0wi8 oo9gr5id lrazzd5p"
        # Find a tags satisfying some condition
        a_tags = self.fb_login.find_elements_by_xpath(f"//a[@class='{CLASS_NAME}']")
        a_tag_wanted = a_tags[0]
        text = a_tag_wanted.text
        return text

    def get_shares_count(self, fbStringToNumber):

        div = self.fb_login
        current_url = self.fb_login.current_url
        if "/posts/" in current_url:
            # This class name identifies the post
            MAIN_POST_CLASS_NAME = "d2edcug0 tr9rh885 oh7imozk abvwweq7 ejjq64ki"
            divs = self.fb_login.find_elements_by_xpath(
                f"//div[@class='{MAIN_POST_CLASS_NAME}']"
            )
            div = divs[0]

        if "/watch/" in current_url:
            # This class name identifies the post
            MAIN_POST_CLASS_NAME = "cwj9ozl2 j83agx80 datstx6m"
            divs = self.fb_login.find_elements_by_xpath(
                f"//div[@class='{MAIN_POST_CLASS_NAME}']"
            )
            div = divs[0]

        CLASS_NAME_POSTS = "d2edcug0 hpfvmrgz qv66sw1b c1et5uql lr9zc1uh a8c37x1j fe6kdd0r mau55g9w c8b282yb keod5gw0 nxhoafnm aigsh9s9 d3f4x2em iv3no6db jq4qci2q a3bd9o3v b1v8xokw m9osqain"
        shares_count = 0
        shares_count_a = div.find_elements_by_xpath(
            f".//span[@class='{CLASS_NAME_POSTS}']"
        )
        for s_c_a in shares_count_a:
            shares_count_a_text = s_c_a.text
            if "compartido" in shares_count_a_text:
                shares_count_text = shares_count_a_text.replace(
                    " veces compartido", ""
                ).replace(" vez compartido", "")
                shares_count = fbStringToNumber.convert_string_to_number(shares_count_text)
                break
        return shares_count

    def get_reactions_count(self, fbStringToNumber):

        div = self.fb_login
        current_url = self.fb_login.current_url
        if "/posts/" in current_url:
            # This class name identifies the post
            MAIN_POST_CLASS_NAME = "d2edcug0 tr9rh885 oh7imozk abvwweq7 ejjq64ki"
            divs = self.fb_login.find_elements_by_xpath(
                f"//div[@class='{MAIN_POST_CLASS_NAME}']"
            )
            div = divs[0]

        if "/watch/" in current_url:
            # This class name identifies the post
            MAIN_POST_CLASS_NAME = "cwj9ozl2 j83agx80 datstx6m"
            divs = self.fb_login.find_elements_by_xpath(
                f"//div[@class='{MAIN_POST_CLASS_NAME}']"
            )
            div = divs[0]
            CLASS_NAME_COMMENTS_DIV = "oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of n00je7tq arfg74bv qs9ysxi8 k77z8yql l9j0dhe7 abiwlrkh p8dawk7l lzcic4wl gmql0nx0 j83agx80 ni8dbmo4 stjgntxs"
            div_comments = div.find_element_by_xpath(
                f".//div[@class='{CLASS_NAME_COMMENTS_DIV}']"
            )
            amount = fbStringToNumber.convert_string_to_number(div_comments.text)
            return amount

        CLASS_NAME = "gpro0wi8 pcp91wgn"
        reactions_count = 0
        reactions_count_span = div.find_elements_by_xpath(
            f".//span[@class='{CLASS_NAME}']"
        )
        if reactions_count_span:
            reactions_count_text = reactions_count_span[0].text
            reactions_count = fbStringToNumber.convert_string_to_number(
                reactions_count_text
            )
        return reactions_count

    def get_comments_count(self, fbStringToNumber):

        div = self.fb_login
        current_url = self.fb_login.current_url
        if "/posts/" in current_url:
            # This class name identifies the post
            MAIN_POST_CLASS_NAME = "d2edcug0 tr9rh885 oh7imozk abvwweq7 ejjq64ki"
            divs = self.fb_login.find_elements_by_xpath(
                f"//div[@class='{MAIN_POST_CLASS_NAME}']"
            )
            div = divs[0]
        if "/watch/" in current_url:
            # This class name identifies the post
            MAIN_POST_CLASS_NAME = "cwj9ozl2 j83agx80 datstx6m"
            divs = self.fb_login.find_elements_by_xpath(
                f"//div[@class='{MAIN_POST_CLASS_NAME}']"
            )
            div = divs[0]

        COMMENTS_SPAN_IN_LINK = "d2edcug0 hpfvmrgz qv66sw1b c1et5uql lr9zc1uh a8c37x1j fe6kdd0r mau55g9w c8b282yb keod5gw0 nxhoafnm aigsh9s9 d3f4x2em iv3no6db jq4qci2q a3bd9o3v b1v8xokw m9osqain"
        COMMENTS_SPAN_IN_VIDEO = "d2edcug0 hpfvmrgz qv66sw1b c1et5uql lr9zc1uh a8c37x1j fe6kdd0r mau55g9w c8b282yb keod5gw0 nxhoafnm aigsh9s9 d9wwppkn mdeji52x e9vueds3 j5wam9gi b1v8xokw m9osqain"
        pot_span_comments_link = div.find_elements_by_xpath(
            f".//span[@class='{COMMENTS_SPAN_IN_LINK}']"
        )
        pot_span_comments_video = div.find_elements_by_xpath(
            f".//span[@class='{COMMENTS_SPAN_IN_VIDEO}']"
        )

        amount = 0
        for c_c_a in pot_span_comments_link + pot_span_comments_video:
            text = c_c_a.text
            if "comentarios" in text:
                if "mil" in text:
                    decimal_n = float(
                        text.replace("comentarios", "")
                        .replace("mil", "")
                        .replace(",", ".")
                        .strip()
                    )
                    amount = int(decimal_n * 1000)
                    break
                amount = int(text.replace("comentarios", "").strip())
                break
            elif "comentario" in text:
                amount = int(text.replace("comentario", "").strip())
                break
            else:
                pass
        return amount

    def get_post_url(self, page_id, post_id):
        return self.urlLink

    def get_post_id(self):
        tokens = self.urlLink.replace("https://www.facebook.com/", "").split("/")
        page_id, post_id = ("", "")
        try:
            page_id = tokens[0]
            post_id = tokens[2]
            try:
                # this is for the case in which the post is a collection of images
                image_id = int(tokens[3])
                post_id = post_id + f"/{image_id}"
            except (ValueError, IndexError):
                pass
        except IndexError:
            print(
                colored(
                    f"ERROR: Page ID and post ID could not be obtainged for {self.urlLink}",
                    "red",
                )
            )
        return post_id, page_id

    def click_to_see_full_text(self):
        CLASS_NAME = "oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gpro0wi8 oo9gr5id lrazzd5p"
        divs = self.fb_login.find_elements_by_xpath(f"//div[@class='{CLASS_NAME}']")
        for div in divs:
            if div.text == "Ver más":
                div.click()
                sleep(1)
                break

    def get_post_message(self):
        # TODO: this function is not capable of extracting emojis
        post_message = ""
        current_url = self.fb_login.current_url
        if "watch" in current_url:

            self.click_to_see_full_text()

            CLASS_NAME_OPTION_0 = "e5nlhep0 nu4hu5il eg9m0zos"
            CLASS_NAME_OPTION_1 = "e5nlhep0"
            try:
                div = self.fb_login.find_element_by_xpath(
                    f"//div[@class='{CLASS_NAME_OPTION_0}']"
                )
            except NoSuchElementException:
                div = self.fb_login.find_element_by_xpath(
                    f"//div[@class='{CLASS_NAME_OPTION_1}']"
                )
            post_message = div.text
            return post_message

        if "/photos/" in current_url:
            CLASS_NAME_DIV = "a8nywdso j7796vcc rz4wbd8a l29c1vbm"
            div = self.fb_login.find_elements_by_xpath(
                f"//div[@class='{CLASS_NAME_DIV}']"
            )
            post_message = div[0].text
            return post_message

        post_message_divs = self.html_bs.find_all(
            "div", {"data-ad-comet-preview": "message"}
        )
        try:
            main_post = post_message_divs[0]
            intern_spans = main_post.find_all("span")
            for i_s in intern_spans:
                intern_divs = i_s.find_all("div")
                for i_d in intern_divs:
                    intern_intern_divs = i_d.find_all("div")
                    for i_i_d in intern_intern_divs:
                        # This allows to extract the text in the post
                        # taking into account the separation of paragraphs
                        intern_text = i_i_d.getText()
                        post_message = post_message + intern_text + "\n"
        except IndexError:
            pass

        return post_message

    def click_to_see_all_reactions(self):
        """
        Click a button to display more information about reactions on the pub
        Returns True if the click was done, False otherwise.
        Constant TEXT_DISPLAYED may need to be changed regularly.
        """
        div = self.fb_login
        current_url = self.fb_login.current_url
        if "/posts/" in current_url:
            # This class name identifies the post
            MAIN_POST_CLASS_NAME = "d2edcug0 tr9rh885 oh7imozk abvwweq7 ejjq64ki"
            divs = self.fb_login.find_elements_by_xpath(
                f"//div[@class='{MAIN_POST_CLASS_NAME}']"
            )
            div = divs[0]
        if "/photos/" in current_url:
            CLASS_NAME_DIV = "bp9cbjyn j83agx80 buofh1pr ni8dbmo4 stjgntxs"
            div = div.find_element_by_xpath(f"//div[@class='{CLASS_NAME_DIV}']")
            div.click()
            return True
        if "/watch/" in current_url:

            # This class name identifies the post
            MAIN_POST_CLASS_NAME = "cwj9ozl2 j83agx80 datstx6m"
            divs = self.fb_login.find_elements_by_xpath(
                f"//div[@class='{MAIN_POST_CLASS_NAME}']"
            )
            div = divs[0]

            CLASS_NAME_DIV = "stjgntxs ni8dbmo4 bkfpd7mw buofh1pr j83agx80 bp9cbjyn"
            div_reactions = div.find_element_by_xpath(
                f".//div[@class='{CLASS_NAME_DIV}']"
            )
            div_reactions.click()

        TEXT_DISPLAYED = "Consulta quién reaccionó a esto"
        spans = div.find_elements_by_xpath(f".//span[@aria-label='{TEXT_DISPLAYED}']")
        for ps in spans:
            try:
                ps.click()
                return True
            except ElementClickInterceptedException:
                continue
        return False

    def get_divs_for_main_reactions(self):
        """
        Once you've clicked on the button to display more inf. about reactions
        you may see "main reactions" and "additional reactions". An addtitional
        reaction is one that needs a button "Más" to be displayed. A main reaction
        is one that is not additional.
        Return a list of divs containing data about main reactions.
        Constant CLASS_NAME may need to be changed regularly.
        """
        CLASS_NAME = "bp9cbjyn rq0escxv j83agx80 pfnyh3mw l9j0dhe7 cehpxlet aodizinl hv4rvrfc ofv0k9yr dati1w0a"
        main_reactions_divs = []
        candidates_divs = self.fb_login.find_elements_by_xpath(
            f"//div[@class='{CLASS_NAME}']"
        )
        for candidate in candidates_divs:
            # next let's verify its text is a number
            # so we know it's a main reaction div
            try:
                text = candidate.text
                if "mil" in text:
                    # 2,3 mil
                    float(text.replace("mil", "").strip().replace(",", "."))
                else:
                    int(text)
                main_reactions_divs.append(candidate)
            except:
                pass
        return main_reactions_divs

    def click_to_see_more_reactions(self):
        """
        Click a button to display information about additional reactions
        Returns True if the click was done, False otherwise.
        Constant CLASS_NAME may need to be changed regularly.
        Constant TEXT_DISPLAYED may need to be changed regularly.
        """
        CLASS_NAME = "q9uorilb l9j0dhe7 j1lvzwm4 ae0w7mvl r9glsfau gbic8f20 tgvbjcpo ni8dbmo4 stjgntxs"
        TEXT_DISPLAYED = "Más"
        potential_blocks = self.fb_login.find_elements_by_xpath(
            f"//div[@class='{CLASS_NAME}']"
        )
        for pb in potential_blocks:
            if TEXT_DISPLAYED in pb.text:
                try:
                    pb.click()
                    sleep(0.25)
                    return True
                except ElementNotInteractableException:
                    # The element is not clickable, if the whole FOR cycle finishes
                    # that means the button 'Más' was not present
                    continue
        return False

    def get_divs_for_additional_reactions(self):
        """
        Once you've clicked on the button to display more inf. about reactions
        you may see "main reactions" and "additional reactions". An addtitional
        reaction is one that needs a button "Más" to be displayed. A main reaction
        is one that is not additional.
        Return a list of divs containing data about additional reactions.
        """
        add_reactions = []
        candidate_divs = self.fb_login.find_elements_by_xpath(
            "//div[@role='menuitemradio']"
        )
        for candidate in candidate_divs:
            # next let's verify its text is a number
            # so we know it's a main reaction div
            try:
                text = candidate.text
                if "mil" in text:
                    # 2,3 mil
                    float(text.replace("mil", "").strip().replace(",", "."))
                else:
                    int(text)
                add_reactions.append(candidate)
            except:
                pass
        return add_reactions

    def identify_reactions(self, divs_with_image):
        """
        Given a list of divs containing each one data about a type of reaction,
        it returns a dict with key-values "type-of-reaction": "times-reacted".
        """
        like = Image.open("./reaction_icons/like.png")
        love = Image.open("./reaction_icons/love.png")
        haha = Image.open("./reaction_icons/haha.png")
        wow = Image.open("./reaction_icons/wow.png")
        sad = Image.open("./reaction_icons/sad.png")
        hate = Image.open("./reaction_icons/hate.png")
        care = Image.open("./reaction_icons/care.png")
        reactions = {
            "likes": 0,
            "loves": 0,
            "hahas": 0,
            "wows": 0,
            "sads": 0,
            "hates": 0,
            "cares": 0,
        }
        for div_w_img in divs_with_image:
            img_tags = div_w_img.find_elements_by_tag_name("img")
            img_src = img_tags[0].get_attribute("src")
            temp_filename = "img_to_be_compared.png"
            # download image into a file
            urlretrieve(img_src, temp_filename)
            # open the image file
            img_to_be_compared = Image.open(temp_filename)

            text = div_w_img.text
            amount = 0
            if "mil" in text:
                amount = float(text.replace("mil", "").strip().replace(",", ".")) * 1000
            else:
                amount = int(text)
            # compare with the reaction image models
            if list(like.getdata()) == list(img_to_be_compared.getdata()):
                reactions["likes"] = amount
            elif list(love.getdata()) == list(img_to_be_compared.getdata()):
                reactions["loves"] = amount
            elif list(haha.getdata()) == list(img_to_be_compared.getdata()):
                reactions["hahas"] = amount
            elif list(wow.getdata()) == list(img_to_be_compared.getdata()):
                reactions["wows"] = amount
            elif list(sad.getdata()) == list(img_to_be_compared.getdata()):
                reactions["sads"] = amount
            elif list(hate.getdata()) == list(img_to_be_compared.getdata()):
                reactions["hates"] = amount
            elif list(care.getdata()) == list(img_to_be_compared.getdata()):
                reactions["cares"] = amount
            os.remove(temp_filename)
        return reactions

    def get_reactions(self):
        # Click on "Consulta quién reaccionó a esto"
        self.click_to_see_all_reactions()
        # Click on "Más"
        # TODO: Fails if the "Más" button is not there, check it's there first
        sleep(2)
        self.click_to_see_more_reactions()
        # Number of reactions for reactions that are not inside the "Más" button
        main_reaction_divs = self.get_divs_for_main_reactions()
        # Number of reactions only for reactions that are inside the "Más" button
        add_reaction_divs = self.get_divs_for_additional_reactions()
        # Identify every number with a kind of reaction
        reactions = self.identify_reactions(main_reaction_divs + add_reaction_divs)

        like_count_fb = reactions["likes"]
        rea_LOVE = reactions["loves"]
        rea_HAHA = reactions["hahas"]
        rea_WOW = reactions["wows"]
        rea_SAD = reactions["sads"]
        rea_ANGRY = reactions["hates"]
        rea_CARE = reactions["cares"]

        return like_count_fb, rea_LOVE, rea_WOW, rea_HAHA, rea_SAD, rea_ANGRY, rea_CARE
