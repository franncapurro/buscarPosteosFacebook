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
import urllib.request
import bs4
import os
import locale
from time import sleep
from datetime import datetime, timedelta
from FacebookStringToNumber import FacebookStringToNumber
from TextOutputFile import TextOutputFile
from selenium.webdriver.common.keys import Keys
from urllib.request import urlretrieve
from selenium.common.exceptions import ElementNotInteractableException
from PIL import Image


class PostFacebook():
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
        url = self.urlLink.replace('videos', 'posts')
        self.fb_login.get(url)
        sleep(5)
        
        body = self.fb_login.find_element_by_xpath('//body')
        body.send_keys(Keys.ESCAPE)
        sleep(1)

        try:
            post = self.fb_login.find_element_by_css_selector('.du4w35lb.l9j0dhe7')
            html = post.get_attribute("innerHTML")
        except Exception as ex:
            print("ERROR" + str(ex))
        return html

    def _getHtmlPost(self, html_raw):
        contenido = None
        if html_raw:
            contenido = bs4.BeautifulSoup(html_raw, 'lxml')
        return contenido

    def SaveHtml(self, base_path):
        post_id, page_id = self.getPostID()
        text_output_file = TextOutputFile(str(self.html_raw))
        text_output_filename = "post_page_" + page_id + "_" + post_id + ".html"
        output_filename_html = os.path.join(base_path, text_output_filename)
        # use a hash to create a unique simpler filename
        hash_object = hashlib.md5(output_filename_html.encode())
        text_output_file.save(f"file_{hash_object.hexdigest()}")

    def ParsePostHTML(self):
        posts = []

        page_name = self.getPageName()
        if page_name is None:
            print('post skip')
            return posts

        posts.append('')  # type

        posts.append(page_name)

        post_id, page_id = self.getPostID()
        posts.append("post_page_" + page_id)
        posts.append(page_id + "_" + post_id)
        posts.append(self.getPostURL(page_id, post_id))

        # post_message
        posts.append(self.getPostMessage())

        # picture
        posts.append(self.getPicture())

        # full_picture
        full_picture, post_picture_descripcion = self.getFullPicture()
        posts.append(full_picture)

        link = ''
        link_domain = ''
        poll_count = 0
        link_div = self.html_bs.find_all('a', {'class': 'oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 datstx6m k4urcfbm'})
        if link_div:
            a_link_tag = link_div[0]
            a_link_href = a_link_tag.get('href')
            a_link_url_query = urllib.parse.urlsplit(a_link_href).query
            link_dict = urllib.parse.parse_qs(a_link_url_query)
            link = link_dict.get('u', [''])[0]
            # link_domain
            link_domain_div = self.html_bs.find_all('span', {'class': 'd2edcug0 hpfvmrgz qv66sw1b c1et5uql b0tq1wua a8c37x1j keod5gw0 nxhoafnm aigsh9s9 tia6h79c fe6kdd0r mau55g9w c8b282yb iv3no6db e9vueds3 j5wam9gi b1v8xokw m9osqain'})
            if link_domain_div:
                link_domain = link_domain_div[0].getText()
            posts[0] = 'link'
        else:
            link_video = self.html_bs.select('video[src]')
            if link_video:
                a_link_href = self.getVideoLink(link_video)
                link_domain = 'facebook.com'
                posts[0] = 'video'
            else:
                link_imagen_tag = self.html_bs.find_all('a', {'class': '_4-eo _2t9n _50z9'})
                if link_imagen_tag:
                    a_link_href = link_imagen_tag[0].get('href')
                    link = "https://www.facebook.com" + a_link_href
                    link_domain = 'facebook.com'
                    posts[0] = 'imagen'
                else:
                    link_imagen_tag = self.html_bs.find_all('a', {'class': '_6k_ _4-eo _5dec _1ktf'})
                    if link_imagen_tag:
                        a_link_href = link_imagen_tag[0].get('href')
                        link = "https://www.facebook.com" + a_link_href
                        link_domain = 'facebook.com'
                        posts[0] = 'imagen'
                    else:
                        link_imagen_tag = self.html_bs.find_all('a', {'class': '_4-eo _2t9n'})
                        if link_imagen_tag:
                            a_link_href = link_imagen_tag[0].get('href')
                            link = "https://www.facebook.com" + a_link_href
                            link_domain = 'facebook.com'
                            posts[0] = 'imagen'
                        else:
                            cabecera_span_tag = self.html_bs.find_all('span', {'class': 'fcg'})
                            for span in cabecera_span_tag:
                                if 'encuesta' in str(span):
                                    posts[0] = 'encuesta'
                                    poll_tag = self.html_bs.find_all('div', {'class': '_204q'})
                                    if poll_tag:
                                        poll_count_text = poll_tag[0].getText().replace('votos', '')
                                        poll_count = self.fbStringToNumber.convertStringToNumber(poll_count_text)                    
                                    break

        posts.append(link)
        posts.append(link_domain)

        # post_published
        post_published_str, post_published_unix, post_published_sql, post_date_argentina = self.getPostDate()
        posts.append(post_published_str) 
        posts.append(post_published_unix)
        posts.append(post_published_sql)
        posts.append(post_date_argentina)

        like_count_fb, rea_LOVE, rea_WOW, rea_HAHA, rea_SAD, rea_ANGRY = self.getReactions(self.fbStringToNumber)

        posts.append(like_count_fb)

        # comments_count_fb
        comments_count = self.getCommentsCount(self.fbStringToNumber)
        posts.append(comments_count)

        # reactions_count_fb
        reactions_count = self.getReactionsCount(self.fbStringToNumber)
        posts.append(reactions_count)

        # shares_count_fb
        shares_count = self.getSharesCount(self.fbStringToNumber)
        posts.append(shares_count)

        # engagement_fb
        try:
            posts.append(comments_count + reactions_count + shares_count)
        except Exception:
            posts.append('')

        posts.append(like_count_fb)
        posts.append(rea_LOVE)
        posts.append(rea_WOW)
        posts.append(rea_HAHA)
        posts.append(rea_SAD)
        posts.append(rea_ANGRY)

        posts.append(post_picture_descripcion)
        posts.append(poll_count)

        titulo = self.getTituloLink()
        subtitulo_post = "" #no existe mas este dato

        posts.append(titulo)
        posts.append(subtitulo_post)

        mencionesLista, hashtagsLista = self.getMencionesHashtags()
        posts.append(mencionesLista)
        posts.append(hashtagsLista)

        video_plays_count = self.getVideosPlaysCount(self.fbStringToNumber)
        posts.append(video_plays_count)

        fb_action_tags_text = self.getFBActionTagsText()
        posts.append(fb_action_tags_text)

        has_emoji = self.getHasEmoji()
        posts.append(has_emoji)

        tiene_hashtags = self.getTieneHashtags(hashtagsLista)

        posts.append(tiene_hashtags)

        tiene_menciones = self.getTieneHashtags(mencionesLista)

        posts.append(tiene_menciones)
        return posts

    #Para Posteos en el dia hay que cambiarlo.
    #viene en formato 24 min o 1 h
    def getPostDate(self):
        locale.setlocale(locale.LC_TIME, 'es_AR')
        a_date = self.html_bs.find_all('a', {'class': 'oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw'})
        if a_date:
            a_date_text = a_date[0].get("aria-label")
            a_date_text = a_date_text.replace('de', '')
            a_date_text = a_date_text.strip()

            if 'h' in a_date_text:
                a_date_text = a_date_text.replace(' ', '')
                a_date_text = a_date_text.replace('h', '')
                hours = -1*int(a_date_text)
                post_date = datetime.now() + timedelta(hours=hours)
            elif 'min' in a_date_text:
                a_date_text = a_date_text.replace(' ', '')
                a_date_text = a_date_text.replace('min', '')
                minutes = -1*int(a_date_text)
                post_date = datetime.now() + timedelta(minutes=minutes)
            elif ' d' in a_date_text:
                a_date_text = a_date_text.replace(' ', '')
                a_date_text = a_date_text.replace('d', '')
                days = -1*int(a_date_text)
                post_date = datetime.now() + timedelta(hours=24*days)
            elif "a las" in a_date_text:
                a_date_text = a_date_text.replace('a las', '')
                post_date = datetime.strptime(a_date_text, '%d %B %Y')+ timedelta(hours=3)
            
            post_published_unix = datetime.timestamp(post_date)
            post_date = datetime.utcfromtimestamp(int(post_published_unix))

            post_date_argentina = post_date.strftime('%Y-%m-%d %H:%M:%S')
            post_published = post_date + timedelta(hours=-3)
            post_published_sql = post_published.strftime("%Y-%m-%d %H:%M:%S")
            
            post_published_str = post_published.replace(microsecond=0).isoformat() + "+0000"
        return post_published_str, post_published_unix, post_published_sql, post_date_argentina

    def getVideoLink(self, link_video):
        link = link_video[0].get('src')
        if link:
            link = link.replace('blob:', '')
        return link

    def getPageName(self):
        # Find a tags satisfying some condition
        class_in_a_tags = []
        a_tags = self.html_bs.find_all('a')
        for a_tag in a_tags:
            class_attr = a_tag.get("class")
            if "oajrlxb2" in class_attr:
                class_in_a_tags.append(a_tag)
        # Find a specific a tag
        index_one_less = 0
        for index, elem in enumerate(class_in_a_tags):
            text = elem.getText()
            if "Información" in text:
                index_one_less = index
                break
        index_wanted = index_one_less + 1
        a_tag_wanted = class_in_a_tags[index_wanted]
        text_wanted = None
        if a_tag_wanted:
            text_wanted = a_tag_wanted.getText()
        return text_wanted

    def getTieneHashtags(self, hashtagsLista):
        tiene_hashtags = False
        if hashtagsLista:
            tiene_hashtags = True
        return tiene_hashtags

    def getHasEmoji(self):
        has_emoji = False
        post_message_div = self.html_bs.find_all('div', {'data-ad-comet-preview': 'message'})
        if post_message_div:
            emoji_tags = post_message_div[0].find_all('span', {'class': 'q9uorilb tbxw36s4 knj5qynh kvgmc6g5 ditlmg2l oygrvhab nvdbi5me fgm26odu gl3lb2sf hhz5lgdu'})
            if emoji_tags:
                has_emoji = True
        return has_emoji

    def getFBActionTagsText(self):
        fb_action_tags_text = ''
        fb_action_tags = self.html_bs.find_all('span', {'class': 'fcg'})
        if fb_action_tags:
            fb_action_tags_text = fb_action_tags[0].getText()
        return fb_action_tags_text

    def getVideosPlaysCount(self, fbStringToNumber):
        video_plays_count = 0
        video_play_count_tags = self.html_bs.find_all('div', {'class': 'lfloat _ohe _50f8'})
        if video_play_count_tags:
            video_play_count_span_text = video_play_count_tags[0].getText().replace('reproducciones', '')
            video_plays_count = fbStringToNumber.convertStringToNumber(video_play_count_span_text)
        else:
            video_play_count_tags = self.html_bs.find_all('span', {'class': '_26fq'})
            if video_play_count_tags:
                video_play_count_span_text = video_play_count_tags[0].getText().replace('reproducciones', '')
                video_plays_count = fbStringToNumber.convertStringToNumber(video_play_count_span_text)
            
        return video_plays_count

    def getMencionesHashtags(self):
        mencionesLista = []
        hashtagsLista = []
        post_message_html = self.html_bs.find_all('div', {'data-ad-comet-preview': 'message'})
        if post_message_html:
            menciones = post_message_html[0].find_all('a', {'class': 'oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl q66pz984 gpro0wi8 b1v8xokw'})
            for mencion in menciones:
                mencionesLista.append(mencion.getText())

            hashtags = post_message_html[0].find_all('span', {'class': '_58cm'})
            for hashtag in hashtags:
                hashtagsLista.append(hashtag.getText())
        return mencionesLista, hashtagsLista

    def getTituloLink(self):
        span_tags = self.html_bs.find_all('span', {'class': 'a8c37x1j ni8dbmo4 stjgntxs l9j0dhe7 ojkyduve'})
        index_minus_one = 0
        for i, span_tag in enumerate(span_tags):
            span_text_inside = span_tag.getText()
            if "Anteriores" in span_text_inside:
                index_minus_one = i
                break
        span_tag_wanted = span_tags[index_minus_one + 1]
        text_wanted = span_tag_wanted.getText()
        return text_wanted

    def getSharesCount(self, fbStringToNumber):
        shares_count = 0
        shares_count_a = self.html_bs.find_all('span', {'class': 'd2edcug0 hpfvmrgz qv66sw1b c1et5uql b0tq1wua a8c37x1j keod5gw0 nxhoafnm aigsh9s9 d9wwppkn fe6kdd0r mau55g9w c8b282yb hrzyx87i jq4qci2q a3bd9o3v b1v8xokw m9osqain'})
        if shares_count_a:
            shares_count_a_text = shares_count_a[1].getText()
            if 'comentario' in shares_count_a_text:
                return shares_count
            shares_count_text = shares_count_a_text.replace(' veces compartido', '').replace(' vez compartido', '')
            shares_count = fbStringToNumber.convertStringToNumber(shares_count_text)
        return shares_count

    def getReactionsCount(self, fbStringToNumber):
        reactions_count = 0
        reactions_count_span = self.html_bs.find_all('span', {'class': 'gpro0wi8 pcp91wgn'})
        if reactions_count_span:
            reactions_count_text = reactions_count_span[0].getText()
            reactions_count = fbStringToNumber.convertStringToNumber(reactions_count_text)
        return reactions_count

    def getCommentsCount(self, fbStringToNumber):
        comments_count = 0
        comments_count_a = self.html_bs.find_all('span', {'class': 'd2edcug0 hpfvmrgz qv66sw1b c1et5uql lr9zc1uh a8c37x1j keod5gw0 nxhoafnm aigsh9s9 fe6kdd0r mau55g9w c8b282yb d3f4x2em iv3no6db jq4qci2q a3bd9o3v b1v8xokw m9osqain'})
        if len(comments_count_a) > 1:
            comments_count_a_text = comments_count_a[1].getText()
            if 'compartido' in comments_count_a_text:
                return comments_count
            comments_count_text = comments_count_a_text.replace(' comentarios', '').replace(' comentario', '')
            comments_count = fbStringToNumber.convertStringToNumber(comments_count_text)
        return comments_count

    def getPostURL(self, page_id, post_id):
        return "https://www.facebook.com/" + page_id + "/posts/" + post_id + "/"

    def getPostID(self):
        page_id = self.urlLink.replace('https://www.facebook.com/', '')
        page_id_split = page_id.split('/')
        page_id = page_id_split[0]
        post_id = page_id_split[2]
        return post_id, page_id

    def getPicture(self):
        picture = ''

        picture_img = self.html_preview_bs.find_all('img', {'class': 'a8c37x1j bixrwtb6'})
        if picture_img:
            picture = picture_img[0].get('src')
            return picture
        
        picture_img_div = self.html_preview_bs.find_all('div', {'class': 'l9j0dhe7 pfnyh3mw aph9nnby'})
        if picture_img_div:
            picture_img = picture_img_div[0].find_all('img')
            if picture_img:
                picture = picture_img[0].get('src')
                a_link_url_query = urllib.parse.urlsplit(picture).query
                link_dict = urllib.parse.parse_qs(a_link_url_query)
                picture = link_dict.get('url', [''])[0]

        return picture

    def getFullPicture(self):
        full_picture = ''
        post_picture_descripcion = ''
        full_picture_img = self.html_bs.find_all('img', {'class': 'i09qtzwb n7fi1qx3 datstx6m pmk7jnqg j9ispegn kr520xx4 k4urcfbm bixrwtb6'})
        if full_picture_img:
            full_picture = full_picture_img[0].get('src')
            a_link_url_query = urllib.parse.urlsplit(full_picture).query
            link_dict = urllib.parse.parse_qs(a_link_url_query)
            full_picture = link_dict.get('url', [''])[0]
            post_picture_descripcion = full_picture_img[0].get('alt')
        return full_picture, post_picture_descripcion

    def getPostMessage(self):
        post_message = ''

        post_message_div = self.html_bs.find_all('div', {'data-ad-comet-preview': 'message'})
        if post_message_div:
            post_message = post_message_div[0].getText()
        
        return post_message

    def click_to_see_all_reactions(self):
        """
        Click a button to display more information about reactions on the pub
        Returns True if the click was done, False otherwise.
        Constant TEXT_DISPLAYED may need to be changed regularly.
        """
        TEXT_DISPLAYED = 'Consulta quién reaccionó a esto'
        for ps in self.fb_login.find_elements_by_tag_name("span"):
            if ps.get_attribute("aria-label") == TEXT_DISPLAYED:
                ps.click()
                return True
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
        candidates_divs = self.fb_login.find_elements_by_xpath(f"//div[@class='{CLASS_NAME}']")
        for candidate in candidates_divs:
            # next let's verify its text is a number
            # so we know it's a main reaction div
            try:
                int(candidate.text)
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
        TEXT_DISPLAYED = 'Más'
        potential_blocks = self.fb_login.find_elements_by_xpath(F"//div[@class='{CLASS_NAME}']")
        for pb in potential_blocks:
            if TEXT_DISPLAYED in pb.text:
                try:
                    pb.click()
                    sleep(0.25)
                    return True
                except ElementNotInteractableException:
                    # The element is not clickable, if the whole for cycle finishes
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
        candidate_divs = self.fb_login.find_elements_by_xpath("//div[@role='menuitemradio']")
        for candidate in candidate_divs:
            try:
            # next let's verify its text is a number
            # so we know it's an additional reaction div
                int(candidate.text)
                add_reactions.append(candidate)
            except:
                pass
        return add_reactions
    
    def identify_reactions(self, divs_with_image):
        """
        Given a list of divs containing each one data about a type of reaction,
        it returns a dict with key-values "type-of-reaction": "times-reacted".
        """
        like = Image.open('like.png')
        love = Image.open('love.png')
        haha = Image.open('haha.png')
        wow = Image.open('wow.png')
        sad = Image.open('sad.png')
        hate = Image.open('hate.png')
        care = Image.open('care.png')
        reactions = {
            "likes": 0,
            "loves": 0,
            "hahas": 0,
            "wows":0,
            "sads": 0,
            "hates": 0,
            "cares": 0,
        }
        for div_w_img in divs_with_image:
            img_tags = div_w_img.find_elements_by_tag_name("img")
            img_src = img_tags[0].get_attribute("src")
            # download image into a file
            urlretrieve(img_src, 'img_to_be_compared.png')
            # open the image file
            img_to_be_compared = Image.open('img_to_be_compared.png')
            # compare with the reaction image models
            if list(like.getdata()) == list(img_to_be_compared.getdata()):
                reactions["likes"] = div_w_img.text
            elif list(love.getdata()) == list(img_to_be_compared.getdata()):
                reactions["loves"] = div_w_img.text
            elif list(haha.getdata()) == list(img_to_be_compared.getdata()):
                reactions["hahas"] = div_w_img.text
            elif list(wow.getdata()) == list(img_to_be_compared.getdata()):
                reactions["wows"] = div_w_img.text
            elif list(sad.getdata()) == list(img_to_be_compared.getdata()):
                reactions["sads"] = div_w_img.text
            elif list(hate.getdata()) == list(img_to_be_compared.getdata()):
                reactions["hates"] = div_w_img.text
            elif list(care.getdata()) == list(img_to_be_compared.getdata()):
                reactions["cares"] = div_w_img.text
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
        reactions = self.identify_reactions(main_reaction_divs+add_reaction_divs)

        like_count_fb = reactions["likes"]
        rea_LOVE = reactions["loves"]
        rea_HAHA = reactions["hahas"]
        rea_WOW = reactions["wows"]
        rea_SAD = reactions["sads"]
        rea_ANGRY = reactions["hates"]
        rea_CARE = reactions["cares"]

        return like_count_fb, rea_LOVE, rea_WOW, rea_HAHA, rea_SAD, rea_ANGRY
