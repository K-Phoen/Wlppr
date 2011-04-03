#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       retriever_base.py
#
#       Classes servant de bases aux retrievers.
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


import os.path
from urllib2 import build_opener, HTTPHandler


class Wlppr:
    """ Classe décrivant un fond d'écran """
    
    def __init__(self, no, name, links):
        self.no = no
        self.name = name
        self.links = links
    
    def getURLForSize(self, sizes):
        """
            Parcoure la liste des tailles disponibles pour le fond d'écran
            et retourne la version la plus proche des préférences de tailles
            définies dans la variable sizes
        """
        
        for size in sizes:
            if size in self.links.keys():
                return self.links[size]
        
        raise ValueError("Contraintes de taille non satisfaites")
    
    def getFilename(self, pattern):
        """
            Retourne le nom du fichier correspondant au wall, en 
            respectant le pattern donné
        """
        
        return pattern.replace('%N', self.name)
    
    def getFullPath(self, pattern):
        """
            Retourne l'adresse complète du fichier correspondant au wall,
            en  respectant le pattern donné.
        """
        
        return os.path.abspath(os.path.expanduser(self.getFilename(pattern)))
    
    def __repr__(self):
        return '#%d : %s (%d link : %s)' % (self.no, self.name,
                                            len(self.links),
                                            ', '.join(self.links.keys()))


class RetrieverBase(object):
    """ Classe de base apportant des "outils" à tous les retrievers """
    
    USER_AGENT = 'WLPPR-FETCHER/0.2'
    
    
    def __init__(self):
        self._reInit()
    
    def retrieve(self):
        """ Méthode à surcharger ! """
        
        pass
    
    def _reInit(self):
        self.wlpprs = []
    
    @staticmethod
    def urlGetContents(url):
        """ Accède à une URL et retourne son contenu """
        
        opener = build_opener(HTTPHandler())
        opener.addheaders = [('User-Agent', RetrieverBase.USER_AGENT)]
        
        return opener.open(url).read()
    
    @staticmethod
    def retrieveWlppr(url, filename):
        """ Récupère un fond d'écran et le stocke """
        
        wlppr_content = RetrieverBase.urlGetContents(url)    
    
        open(filename, 'wb').write(wlppr_content)
    
    def parseTitle(self, data_title):
        """
            Récupère le numéro et le titre d'un fond d'écran
            NB : les titres sont de la forme "Episode #999 : Here is the title"
        """
        
        try:
            data = data_title.split(' : ')
            
            no = int(data[0].split('#')[1])
            title = data[1]
        except (IndexError, ValueError):
            no = -1
            title = 'Titre inconnu'
        
        return (no, title)