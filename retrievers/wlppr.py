#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       wlppr.py
#
#       Classes permettant d'accéder aux fonds d'écran du site Wlppr.com
#       
#       Copyright 2011 Kévin Gomez <contact@kevingomez.fr>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from xml.dom import minidom
import re

from retriever_base import Wlppr, RetrieverBase


class RecentWlpprRetriever(RetrieverBase):
    """
        Classe permettant de récupérer les N derniers fonds d'écran
        parus sur le site Wlppr.com
    """
    
    NB_ITEMS = 3
    FEED_URL = 'http://feeds.feedburner.com/wlppr'
    

    def retrieve(self):
        """
            Retourne les nb derniers fonds d'écran contenus dans le flux
            du site.
        """
        
        nb_left = self.NB_ITEMS
        feed_content = RetrieverBase.urlGetContents(self.FEED_URL)
        
        parser = minidom.parseString(feed_content)
        
        for item in parser.getElementsByTagName('entry'):
            if nb_left <= 0:
                break
            
            # récupération du titre
            try:
                data_title = self.getText(item.getElementsByTagName('title')[0])
            except IndexError: # pas de titre spécifié
                data_title = ''
            
            # séparation du numéro du wlppr et du titre en lui-même
            # NB : les titres sont de la forme "Episode #999 : Here is the title"
            no, title = self.parseTitle(data_title)
            
            # récupération des liens
            try:
                data_links = self.getText(item.getElementsByTagName('content')[0])
                links = self.parseLinks(data_links)
            except IndexError: # pas de titre spécifié
                links = {}
            
            if not len(links) == 0:
                self.wlpprs.append(Wlppr(no, title, links))
                
                nb_left -= 1
        
        # on trie les wlpprs selon leur numéro (même si en principe ils 
        # sont déjà triés)
        self.wlpprs.sort(lambda x, y : y .no - x.no)
    
    def parseLinks(self, html):
        """ Récupère les liens des fonds d'écrans et leur taille """
        
        html = '<foo>%s</foo>' % html
        parser = minidom.parseString(html)
        links = {}
        
        p = parser.getElementsByTagName('p')
        if not len(p) == 2: # on est censé avoir deux paragraphes
            return links
        
        # récupération de la "grosse miniature"
        try:
            links['mini'] = p[0].childNodes[0].getAttribute('src')
        except:
            pass
        
        # récupération des différentes versions (tailles) du wlppr
        for li in p[1].getElementsByTagName('li'):
            try:
                size = self.getText(li.childNodes[0])
                link = li.childNodes[0].getAttribute('href')
                
                links[size] = link
            except IndexError:
                continue
        
        return links
    
    def getText(self, element):
        return element.childNodes[0].nodeValue


class RandomWlpprRetriever(RetrieverBase):
    """
        Classe permettant de récupérer un fond d'écran aléatoire via le
        site Wlppr.com
    """
    
    WLPPR_BASE_URL = 'http://wlppr.com'
    WLPPR_URL = 'http://wlppr.com/shuffle'
    WLPPR_TITLE_REGEX = '<h1><a href=".*">(.*)</a></h1>'
    WLPPR_LINKS_ZONE_REGEX = '<div id="downloads">(.*)</div>'
    WLPPR_LINKS_REGEX = '<a href="(.*?)">(.*?)</a>'
    
    
    def retrieve(self):
        """
            Récupère un fond d'écran aléatoire
        """
        
        page_content = RetrieverBase.urlGetContents(self.WLPPR_URL)
        
        # récupération du titre
        try:
            data_title = re.compile(self.WLPPR_TITLE_REGEX) \
                           .findall(page_content)[0]
        except IndexError:
            data_title = ''
        
        no, title = self.parseTitle(data_title)
        
        # récupération des différentes versions (tailles) du wlppr
        links_zone = re.compile(self.WLPPR_LINKS_ZONE_REGEX) \
                       .findall(page_content)[0]
        links = self.parseLinks(links_zone)
        
        if not len(links) == 0:
            self.wlpprs.append(Wlppr(no, title, links))
    
    def parseLinks(self, html):
        """ Récupère les liens des fonds d'écrans et leur taille """
        
        links = {}
        
        data_links = re.compile(self.WLPPR_LINKS_REGEX).findall(html)
        for url_part, size in data_links:
            links[size] = '%s%s' % (self.WLPPR_BASE_URL, url_part)
        
        return links