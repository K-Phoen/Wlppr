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
import gconf

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


def setWallpaper(path):
    """
        Utilise l'image à l'adresse donnée pour changer le fond d'écran
    """
    
    client = gconf.client_get_default()
    client.set_string('/desktop/gnome/background/picture_filename',
                      path)

def getRetriever(site, mode):
    """
        Retourne l'instance du retriever à utiliser en fonction du choix
        de l'utilisateur (site d'origine et mode voulu)
    """
    
    if not Config.SITES.has_key(site):
        raise NameError("Site inconnu : %s" % site)
    
    if not Config.SITES[site].has_key(mode):
        raise NameError("Mode non disponible pour le site %s. Liste des modes supportés : %s"
                        % (site, ', '.join(Config.SITES[site].keys())))
    
    if site == 'fs':
        return Config.SITES[site][mode](Config.WALLPAPERS_DIR)
    
    return Config.SITES[site][mode]()