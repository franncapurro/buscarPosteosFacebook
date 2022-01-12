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

import hashlib
import locale
import os
import urllib.request
from datetime import datetime, timedelta
from time import sleep
from urllib.request import urlretrieve

import bs4
from PIL import Image
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        ElementNotInteractableException)
from selenium.webdriver.common.keys import Keys
from termcolor import colored

from FacebookStringToNumber import FacebookStringToNumber
from TextOutputFile import TextOutputFile


class PostFacebook:
    def __init__(self, urlLink, fb_login, html_preview):
        self.urlLink = urlLink
        self.fb_login = fb_login
        # HTML obtained from search page
        self.html_preview = html_preview
        self.html_preview_bs = self._getHtmlPost(html_preview)
        # HTML obtained from the publication specific link
        self.html_raw = self._getHtmlFacebook()
        self.html_bs = self._getHtmlPost(self.html_raw)

        self.fbStringToNumber = FacebookStringToNumber()

    def _getHtmlFacebook(self):
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

    def _getHtmlPost(self, html_raw):
        contenido = None
        if html_raw:
            contenido = bs4.BeautifulSoup(html_raw, "lxml")
        return contenido

    def SaveHtml(self, base_path):
        post_id, page_id = self.getPostID()
        text_output_file = TextOutputFile(str(self.html_raw))
        text_output_filename = "post_page_" + page_id + "_" + post_id + ".html"
        output_filename_html = os.path.join(base_path, text_output_filename)
        # use a hash to create a unique simpler filename
        hash_object = hashlib.md5(output_filename_html.encode())
        text_output_file.save(f"file_{hash_object.hexdigest()}")
        return f"file_{hash_object.hexdigest()}"

    def ParsePostHTML(self):
        posts = []

        page_name = self.getPageName()
        if page_name is None:
            print(colored("ERROR: page name could not be obtained", "red"))
            return posts
        # type
        posts.append("")
        # medio
        posts.append(page_name)

        post_id, page_id = self.getPostID()
        # by
        posts.append(page_id)
        # post_id
        posts.append(post_id)
        post_url = self.getPostURL(page_id, post_id)
        # post_link
        posts.append(post_url)

        post_message = self.getPostMessage()
        # post_message
        posts.append(post_message)

        # # picture
        # picture = self.getPicture()
        # posts.append(picture)

        # # full_picture
        # full_picture, post_picture_descripcion = self.getFullPicture()
        # posts.append(full_picture)

        link = ""
        link_domain = ""
        poll_count = 0
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
            # link_domain
            link_domain_div = self.html_bs.find_all(
                "span",
                {
                    "class": "d2edcug0 hpfvmrgz qv66sw1b c1et5uql b0tq1wua a8c37x1j keod5gw0 nxhoafnm aigsh9s9 tia6h79c fe6kdd0r mau55g9w c8b282yb iv3no6db e9vueds3 j5wam9gi b1v8xokw m9osqain"
                },
            )
            if link_domain_div:
                link_domain = link_domain_div[0].getText()
            posts[0] = "link"
        else:
            link_video = self.html_bs.select("video[src]")
            if link_video:
                a_link_href = self.getVideoLink(link_video)
                link_domain = "facebook.com"
                posts[0] = "video"
            else:
                link_imagen_tag = self.html_bs.find_all(
                    "a", {"class": "_4-eo _2t9n _50z9"}
                )
                if link_imagen_tag:
                    a_link_href = link_imagen_tag[0].get("href")
                    link = "https://www.facebook.com" + a_link_href
                    link_domain = "facebook.com"
                    posts[0] = "imagen"
                else:
                    link_imagen_tag = self.html_bs.find_all(
                        "a", {"class": "_6k_ _4-eo _5dec _1ktf"}
                    )
                    if link_imagen_tag:
                        a_link_href = link_imagen_tag[0].get("href")
                        link = "https://www.facebook.com" + a_link_href
                        link_domain = "facebook.com"
                        posts[0] = "imagen"
                    else:
                        link_imagen_tag = self.html_bs.find_all(
                            "a", {"class": "_4-eo _2t9n"}
                        )
                        if link_imagen_tag:
                            a_link_href = link_imagen_tag[0].get("href")
                            link = "https://www.facebook.com" + a_link_href
                            link_domain = "facebook.com"
                            posts[0] = "imagen"
                        else:
                            cabecera_span_tag = self.html_bs.find_all(
                                "span", {"class": "fcg"}
                            )
                            for span in cabecera_span_tag:
                                if "encuesta" in str(span):
                                    posts[0] = "encuesta"
                                    poll_tag = self.html_bs.find_all(
                                        "div", {"class": "_204q"}
                                    )
                                    if poll_tag:
                                        poll_count_text = (
                                            poll_tag[0].getText().replace("votos", "")
                                        )
                                        poll_count = (
                                            self.fbStringToNumber.convertStringToNumber(
                                                poll_count_text
                                            )
                                        )
                                    break
        # link
        posts.append(link)
        # posts.append(link_domain)

        # post_published
        (
            post_published_str,
            post_published_unix,
            post_published_sql,
            post_date_argentina,
        ) = self.getPostDate()
        # post_published
        posts.append(post_published_str)
        # # post_published_unix
        # posts.append(post_published_unix)
        # # post_published_sql
        # posts.append(post_published_sql)
        # # post_hora_argentina
        # posts.append(post_date_argentina)

        (
            like_count_fb,
            rea_LOVE,
            rea_WOW,
            rea_HAHA,
            rea_SAD,
            rea_ANGRY,
        ) = self.getReactions(self.fbStringToNumber)
        # like_count_fb
        posts.append(like_count_fb)

        # comments_count_fb
        comments_count = self.getCommentsCount(self.fbStringToNumber)
        # comments_count_fb
        posts.append(comments_count)

        reactions_count = self.getReactionsCount(self.fbStringToNumber)
        # reactions_count_fb
        posts.append(reactions_count)

        shares_count = self.getSharesCount(self.fbStringToNumber)
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

        # posts.append(post_picture_descripcion)
        # posts.append(poll_count)

        # titulo = self.getTituloLink()
        # subtitulo_post = "" #no existe mas este dato
        # # titulo_link
        # posts.append(titulo)
        # # subtitulo_link
        # posts.append(subtitulo_post)

        # mencionesLista, hashtagsLista = self.getMencionesHashtags()
        # # menciones
        # posts.append(mencionesLista)
        # # hashtags
        # posts.append(hashtagsLista)

        # video_plays_count = self.getVideosPlaysCount(self.fbStringToNumber)
        # # video_plays_count
        # posts.append(video_plays_count)

        # fb_action_tags_text = self.getFBActionTagsText()
        # # fb_action_tags_text
        # posts.append(fb_action_tags_text)

        # has_emoji = self.getHasEmoji()
        # # has_emoji
        # posts.append(has_emoji)

        # tiene_hashtags = self.getTieneHashtags(hashtagsLista)
        # # tiene_hashtags
        # posts.append(tiene_hashtags)

        # tiene_menciones = self.getTieneHashtags(mencionesLista)
        # # tiene_menciones
        # posts.append(tiene_menciones)
        return posts

    def getPostDate(self):
        """
        The date may be shown in any of the following ways:
        3 de diciembre de 2021
        14 de diciembre de 2021 a las 15:30
        2 días
        1 min
        8 h
        Hace un momento
        """
        locale.setlocale(locale.LC_TIME, "es_AR")
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
                post_date = datetime.strptime(
                    text_in_new_format, "%d %B %Y"
                )
            elif len(tokens) == 2 and "momento" in tokens:
                # Hace un momento
                post_date = datetime.now()
            elif len(tokens) == 5 and "de" in [tokens[1], tokens[3]]:
                # 3 de diciembre de 2021
                day, month, year = tokens[0], tokens[2], tokens[4]
                text_in_new_format = f"{day} {month} {year}"
                post_date = datetime.strptime(
                    text_in_new_format, "%d %B %Y"
                )
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

    def getVideoLink(self, link_video):
        link = link_video[0].get("src")
        if link:
            link = link.replace("blob:", "")
        return link

    def getPageName(self):
        CLASS_NAME = "oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gpro0wi8 oo9gr5id lrazzd5p"
        # Find a tags satisfying some condition
        a_tags = self.fb_login.find_elements_by_xpath(f"//a[@class='{CLASS_NAME}']")
        a_tag_wanted = a_tags[0]
        text = a_tag_wanted.text
        return text

    def getTieneHashtags(self, hashtagsLista):
        tiene_hashtags = False
        if hashtagsLista:
            tiene_hashtags = True
        return tiene_hashtags

    def getHasEmoji(self):
        has_emoji = False
        post_message_div = self.html_bs.find_all(
            "div", {"data-ad-comet-preview": "message"}
        )
        if post_message_div:
            emoji_tags = post_message_div[0].find_all(
                "span",
                {
                    "class": "q9uorilb tbxw36s4 knj5qynh kvgmc6g5 ditlmg2l oygrvhab nvdbi5me fgm26odu gl3lb2sf hhz5lgdu"
                },
            )
            if emoji_tags:
                has_emoji = True
        return has_emoji

    def getFBActionTagsText(self):
        fb_action_tags_text = ""
        fb_action_tags = self.html_bs.find_all("span", {"class": "fcg"})
        if fb_action_tags:
            fb_action_tags_text = fb_action_tags[0].getText()
        return fb_action_tags_text

    def getVideosPlaysCount(self, fbStringToNumber):
        video_plays_count = 0
        video_play_count_tags = self.html_bs.find_all(
            "div", {"class": "lfloat _ohe _50f8"}
        )
        if video_play_count_tags:
            video_play_count_span_text = (
                video_play_count_tags[0].getText().replace("reproducciones", "")
            )
            video_plays_count = fbStringToNumber.convertStringToNumber(
                video_play_count_span_text
            )
        else:
            video_play_count_tags = self.html_bs.find_all("span", {"class": "_26fq"})
            if video_play_count_tags:
                video_play_count_span_text = (
                    video_play_count_tags[0].getText().replace("reproducciones", "")
                )
                video_plays_count = fbStringToNumber.convertStringToNumber(
                    video_play_count_span_text
                )

        return video_plays_count

    def getMencionesHashtags(self):
        mencionesLista = []
        hashtagsLista = []
        post_message_html = self.html_bs.find_all(
            "div", {"data-ad-comet-preview": "message"}
        )
        if post_message_html:
            menciones = post_message_html[0].find_all(
                "a",
                {
                    "class": "oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl q66pz984 gpro0wi8 b1v8xokw"
                },
            )
            for mencion in menciones:
                mencionesLista.append(mencion.getText())

            hashtags = post_message_html[0].find_all("span", {"class": "_58cm"})
            for hashtag in hashtags:
                hashtagsLista.append(hashtag.getText())
        return mencionesLista, hashtagsLista

    def getTituloLink(self):
        CLASS_NAME = "a8c37x1j ni8dbmo4 stjgntxs l9j0dhe7 ojkyduve"
        text_wanted = ""
        span_tags = self.html_bs.find_all("span", {"class": CLASS_NAME})
        index_minus_one = 0
        for i, span_tag in enumerate(span_tags):
            span_text_inside = span_tag.getText()
            if "Anteriores" in span_text_inside:
                index_minus_one = i
                try:
                    span_tag_wanted = span_tags[index_minus_one + 1]
                    text_wanted = span_tag_wanted.getText()
                    break
                except IndexError:
                    continue
        return text_wanted

    def getSharesCount(self, fbStringToNumber):
        shares_count = 0
        shares_count_a = self.html_bs.find_all(
            "span",
            {
                "class": "d2edcug0 hpfvmrgz qv66sw1b c1et5uql b0tq1wua a8c37x1j keod5gw0 nxhoafnm aigsh9s9 d9wwppkn fe6kdd0r mau55g9w c8b282yb hrzyx87i jq4qci2q a3bd9o3v b1v8xokw m9osqain"
            },
        )
        if shares_count_a:
            shares_count_a_text = shares_count_a[1].getText()
            if "comentario" in shares_count_a_text:
                return shares_count
            shares_count_text = shares_count_a_text.replace(
                " veces compartido", ""
            ).replace(" vez compartido", "")
            shares_count = fbStringToNumber.convertStringToNumber(shares_count_text)
        return shares_count

    def getReactionsCount(self, fbStringToNumber):
        reactions_count = 0
        reactions_count_span = self.html_bs.find_all(
            "span", {"class": "gpro0wi8 pcp91wgn"}
        )
        if reactions_count_span:
            reactions_count_text = reactions_count_span[0].getText()
            reactions_count = fbStringToNumber.convertStringToNumber(
                reactions_count_text
            )
        return reactions_count

    def getCommentsCount(self, fbStringToNumber):
        COMMENTS_SPAN_IN_LINK = "d2edcug0 hpfvmrgz qv66sw1b c1et5uql lr9zc1uh a8c37x1j fe6kdd0r mau55g9w c8b282yb keod5gw0 nxhoafnm aigsh9s9 d3f4x2em iv3no6db jq4qci2q a3bd9o3v b1v8xokw m9osqain"
        COMMENTS_SPAN_IN_VIDEO = "d2edcug0 hpfvmrgz qv66sw1b c1et5uql lr9zc1uh a8c37x1j fe6kdd0r mau55g9w c8b282yb keod5gw0 nxhoafnm aigsh9s9 d9wwppkn mdeji52x e9vueds3 j5wam9gi b1v8xokw m9osqain"
        pot_span_comments_link = self.html_bs.find_all("span", {"class": COMMENTS_SPAN_IN_LINK},)
        pot_span_comments_video = self.html_bs.find_all("span", {"class": COMMENTS_SPAN_IN_VIDEO},)

        amount = 0
        for c_c_a in pot_span_comments_link + pot_span_comments_video:
            text = c_c_a.getText()
            if "comentarios" in text:
                if "mil" in text:
                    decimal_n = float(text.replace("comentarios", "").replace("mil", "").replace(",", ".").strip())
                    amount = int(decimal_n*1000)
                    break
                amount = int(text.replace("comentarios", "").strip())
                break
            elif "comentario" in text:
                amount = int(text.replace("comentario", "").strip())
                break
            else:
                pass
        return amount

    def getPostURL(self, page_id, post_id):
        return self.urlLink

    def getPostID(self):
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

    def getPicture(self):
        picture = ""

        picture_img = self.html_preview_bs.find_all(
            "img", {"class": "a8c37x1j bixrwtb6"}
        )
        if picture_img:
            picture = picture_img[0].get("src")
            return picture

        picture_img_div = self.html_preview_bs.find_all(
            "div", {"class": "l9j0dhe7 pfnyh3mw aph9nnby"}
        )
        if picture_img_div:
            picture_img = picture_img_div[0].find_all("img")
            if picture_img:
                picture = picture_img[0].get("src")
                a_link_url_query = urllib.parse.urlsplit(picture).query
                link_dict = urllib.parse.parse_qs(a_link_url_query)
                picture = link_dict.get("url", [""])[0]

        return picture

    def getFullPicture(self):
        full_picture = ""
        post_picture_descripcion = ""
        full_picture_img = self.html_bs.find_all(
            "img",
            {
                "class": "i09qtzwb n7fi1qx3 datstx6m pmk7jnqg j9ispegn kr520xx4 k4urcfbm bixrwtb6"
            },
        )
        if full_picture_img:
            full_picture = full_picture_img[0].get("src")
            a_link_url_query = urllib.parse.urlsplit(full_picture).query
            link_dict = urllib.parse.parse_qs(a_link_url_query)
            full_picture = link_dict.get("url", [""])[0]
            post_picture_descripcion = full_picture_img[0].get("alt")
        return full_picture, post_picture_descripcion

    def getPostMessage(self):
        # TODO: this function fails for publication pages that are facebook videos or facebook photos
        # TODO: this function is not capable of extracting emojis
        post_message = ""

        if "watch" in self.urlLink:
            CLASS_NAME = (
                "a8c37x1j ni8dbmo4 stjgntxs l9j0dhe7 ltmttdrg g0qnabr5 r8blr3vg"
            )
            span = self.fb_login.find_elements_by_xpath(
                f"//span[@class='{CLASS_NAME}']"
            )
            post_message = span.text
            return post_message
        
        if "/photos/" in self.urlLink:
            CLASS_NAME = (
                "a8nywdso j7796vcc rz4wbd8a l29c1vbm"
            )
            divs = self.fb_login.find_elements_by_xpath(
                f"//div[@class='{CLASS_NAME}']"
            )
            for d in divs:
                text = d.text
                return text

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
        TEXT_DISPLAYED = "Consulta quién reaccionó a esto"
        for ps in self.fb_login.find_elements_by_tag_name("span"):
            if ps.get_attribute("aria-label") == TEXT_DISPLAYED:
                try:
                    ps.click()
                    return True
                except ElementClickInterceptedException:
                    continue
        print(colored(f"ERROR: button {TEXT_DISPLAYED} not found", "red"))
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

    def getReactions(self, fbStringToNumber):
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

        return like_count_fb, rea_LOVE, rea_WOW, rea_HAHA, rea_SAD, rea_ANGRY
