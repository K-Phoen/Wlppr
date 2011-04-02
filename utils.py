#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       utils.py
#
#       Quelques fonctions diverses utilisées par le script principal
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


from sys import stderr
import gconf, os.path

from config import Config
from retrievers.retriever_base import RetrieverBase


def chat(msg, error=False):
    """
        Affiche un message su le mode verbose est activé et sur la
        sortie d'erreur si error vaut true
    """

    if not Config.VERBOSE:
        return
    
    if error:
        print >> stderr, msg
    else:
        print msg


def setWallpaper(url):
    """
        Rècupère l'image à l'url donnée et définit l'image s'y trouvant
        comme fond d'écran
    """
    
    path = os.path.abspath(os.path.expanduser(Config.WLPPR_FILE))
    
    RetrieverBase.retrieveWlppr(url, path)
    
    client = gconf.client_get_default()
    client.set_string('/desktop/gnome/background/picture_filename',
                      path)

def chooseWallpaperBySize(wlppr, sizes):
    """
        Parcoure la liste des tailles disponibles pour le fond d'écran
        et retourne la version la plus proche des préférences de tailles
        définies dans la variable sizes
    """
    
    for size in sizes:
        if size in wlppr.links.keys():
            return wlppr.links[size]
    
    return None