#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       wlppr.py
#
#       Permet d'utiliser des fond d'écrans du site wlppr.com et
#       wallbase.cc
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


from urllib2 import URLError
from optparse import OptionParser
from sys import exit
import re

from config import Config
from retrievers.retriever_base import Wlppr, RetrieverBase
from retrievers.wlppr import RandomWlpprRetriever, RecentWlpprRetriever
from utils import chat, setWallpaper, chooseWallpaperBySize


def main():
    """ Programme principal """

    # Définition des options possibles
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage)

    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=True,
                      help=u"Affiche des messages sur le deroulement "\
                           u"des opérations [défaut]")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose",
                      help=u"Fait taire le programme")
    parser.add_option("-m", "--mode",
                      default="random", type="choice",
                      choices = ["random", "latest"], 
                      help=u"Mode de récuparation : random, latest "\
                           u"[défault : %default]")

    # récupération des options
    options, args = parser.parse_args()

    # traitement des options
    Config.VERBOSE = options.verbose
    Config.WLPPR_TO_RETRIEVE = Config.RANDOM_WLPPR if options.mode == 'random' else \
                               Config.LATEST_WLPPR

    # lancement de la récupération du wlppr
    retriever = RandomWlpprRetriever() \
                if Config.WLPPR_TO_RETRIEVE is Config.RANDOM_WLPPR else \
                RecentWlpprRetriever()
    
    chat('[-] Téléchargement de la liste des fonds d\'écran ...')
    
    try:
        retriever.retrieve()
        
        if len(retriever.wlpprs) == 0:
            url = None
        else:
            url = chooseWallpaperBySize(retriever.wlpprs[0], Config.PREFERED_SIZES)
    except URLError ,e:
        chat('[!] Téléchargement impossible : %s' % e, True)
    
    chat('[-] Fonds d\'écran trouvés')
    
    if url is None:
        chat('[!] Aucun fond d\'écran correspondant aux contraintes de taille trouvé', True)
        exit(1)
    
    chat('[-] Changement du fond d\'écran ...')
    
    setWallpaper(url)
    
    chat('[+] Fond d\'écran mis en place !')


if __name__ == '__main__':
	main()
