#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       wallbase.py
#
#       Classes permettant d'accéder aux fonds d'écran du site wallbase.cc
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


import re

from retriever_base import Wlppr, RetrieverBase


class RandomWallbaseRetriever(RetrieverBase):
    """
        Classe permettant de récupérer un fond d'écran aléatoire via le
        site wallbase.cc
    """
    
    WALLBASE_URL = 'http://wallbase.cc/random'    
    
    WALL_PAGE_REGEX = '<a href="(.*)" id="drg_thumb[0-9]+" class="thdraggable thlink" target="_blank">.*</a>'
    TITLE_REGEX = '<title>(.*)</title>'
    TITLE_DATA_REGEX = '(.+) \- Wallpaper \(#(\d+)\) / Wallbase\.cc'
    DL_LINK_REGEX = '<div id="bigwall" class="right">.*<img src=\'(.*)\' alt="(.*)" />.*</div>'
    
    
    def retrieve(self):
        """
            Récupère un fond d'écran aléatoire
        """
        
        self._reInit()
        
        page_content = RetrieverBase.urlGetContents(self.WALLBASE_URL)
        
        # récupération de l'url de la page du wall
        try:
            url_wall_page = re.compile(self.WALL_PAGE_REGEX).findall(page_content)[0]
        except IndexError:
            return
        
        # exploration de la page du wall pour trouver les infos intéressantes ...
        wall_page = RetrieverBase.urlGetContents(url_wall_page)
        
        try:
            data_title = re.compile(self.TITLE_REGEX).findall(wall_page)[0]
        except IndexError:
            data_title = ''
        
        no, title = self.parseTitle(data_title)
        
        # recherche du lien de téléchargement et de la taille du wall
        try:
            link, size_data = re.compile(self.DL_LINK_REGEX, re.DOTALL).findall(wall_page)[0]
            
            size = size_data.split('/')[1].strip('Wallpaper').strip()
        except IndexError:
            return
        
        self.wlpprs.append(Wlppr(no, title, { size: link }))
    
    def parseTitle(self, data_title):
        """
            Récupère le numéro et le titre d'un fond d'écran
            NB : les titres sont de la forme "Apple Inc. mac think  - Wallpaper (#72648) / Wallbase.cc"
        """
        
        try:
            title, no = re.compile(self.TITLE_DATA_REGEX).findall(data_title)[0]
        except IndexError:
            no, title = -1, 'Titre inconnu'
        
        return (int(no), title.strip())