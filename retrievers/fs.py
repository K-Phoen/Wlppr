#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       fs.py
#
#       Classes permettant d'accéder aux fonds d'écran contenus dans un
#       dossier
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


import random

from PIL import Image
from os import listdir, path
from os.path import isfile, abspath, expanduser

from retriever_base import Wlppr, RetrieverBase


class RandomFsRetriever(RetrieverBase):
    """
        Classe permettant de récupérer un fond d'écran aléatoire en
        explorant le contenu d'un dossier
    """
    
    def __init__(self, wallpapers_dir):
        super(RandomFsRetriever, self).__init__()
        
        self.wallpapers_dir = abspath(expanduser(wallpapers_dir))
    
    def retrieve(self):
        """
            Récupère un fond d'écran aléatoire
        """
        
        self._reInit()
        
        filename = random.choice([x for x in listdir(self.wallpapers_dir)
                                 if isfile(path.join(self.wallpapers_dir, x))]) 
        
        no, title, size, link = self.getInfos(filename)
        
        if no is None:
            return
        
        self.wlpprs.append(Wlppr(no, title, { size: link }))
    
    def getInfos(self, filename):
        
        no = 1 # osef
        link = path.join(self.wallpapers_dir, filename)
        
        try:
            im = Image.open(link)
        except IOError, e:
            return (None, None, None, None)

        return (no, filename, '%dx%d' % im.size, link)