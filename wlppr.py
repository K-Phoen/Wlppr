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

from config import Config
from retrievers.retriever_base import Wlppr, RetrieverBase
from retrievers.wlppr import RandomWlpprRetriever, RecentWlpprRetriever
from utils import chat, setWallpaper, chooseWallpaperBySize, getRetriever


def main():
    """ Programme principal """

    # Définition des options possibles
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage)

    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=Config.VERBOSE,
                      help=u"Affiche des messages sur le deroulement "\
                           u"des opérations")
    parser.add_option("-q", "--quiet", default=Config.VERBOSE,
                      action="store_false", dest="verbose",
                      help=u"Fait taire le programme")
    parser.add_option("-t", "--tries", default=Config.MAX_TRIES,
                      type="int", dest="nb_tries",
                      help=u"nombre maximum d'essais pour la recherche du wall "\
                           u"[défault : %default]")
    parser.add_option("-s", "--site",
                      default="wlppr", type="choice",
                      choices = ["wlppr", "wallbase"], 
                      help=u"Site d'origine : wlppr (Wlppr.com), wallbase (wallbase.cc) "\
                           u"[défault : %default]")
    parser.add_option("-m", "--mode",
                      default="random", type="choice",
                      choices = ["random", "latest", "top"], 
                      help=u"Mode de récuparation : random, latest, top "\
                           u"[défault : %default]")

    # récupération des options
    options, args = parser.parse_args()

    # traitement des options
    Config.VERBOSE = options.verbose
    Config.MAX_TRIES = options.nb_tries

    # lancement de la récupération du wlppr
    retriever = getRetriever(options.site, options.mode)
    
    i = 0
    while i < Config.MAX_TRIES:
        chat('[-] Essai n°%d' % (i+1))
        
        i += 1
        
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
            continue
        
        chat('[-] Changement du fond d\'écran ...')
        
        setWallpaper(url)
        
        chat('[+] Fond d\'écran mis en place !')
        
        break


if __name__ == '__main__':
	main()
