#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       wlppr.py
#
#       Permet d'utiliser des fond d'écrans du site wlppr.com
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


from urllib2 import build_opener, HTTPHandler, URLError
from optparse import OptionParser
from xml.dom import minidom
from sys import stderr, exit
import gconf, os.path, re


class Config:
    """ Classe "conteneur" pour le stockage de la configuration """

    RANDOM_WLPPR = 0x01
    LATEST_WLPPR = 0x02

    WLPPR_TO_RETRIEVE = RANDOM_WLPPR
    # le wall téléchargé sera enregistré ici
    WLPPR_FILE = '~/.wlppr.jpg'
    # liste des tailles favorites (par ordre de préférences décroissantes)
    PREFERED_SIZES = ['1600x1200']

    VERBOSE = False


class Wlppr:
    """ Classe décrivant un fond d'écran """
    
    def __init__(self, no, name, links):
        self.no = no
        self.name = name
        self.links = links
    
    def __repr__(self):
        return '#%d : %s (%d)' % (self.no, self.name, len(self.links))


class WlpprRetrieverBase:
    """ Classe de base apportant des "outils" à tous les retrievers """
    
    USER_AGENT = 'WLPPR-FETCHER/0.1'
    WLPPR_BASE_URL = 'http://wlppr.com'
    
    
    def __init__(self):
        self.wlpprs = []
    
    def retrieve(self):
        """ Méthode à surcharger ! """
        
        return []
    
    @staticmethod
    def urlGetContents(url):
        """ Accède à une URL et retourne son contenu """
        
        opener = build_opener(HTTPHandler())
        opener.addheaders = [('User-Agent', WlpprRetrieverBase.USER_AGENT)]
        
        return opener.open(url).read()
    
    @staticmethod
    def retrieveWlppr(url, filename):
        """ Récupère un fond d'écran et le stocke """
        
        wlppr_content = WlpprRetrieverBase.urlGetContents(url)    
    
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


class FeedRecentWlpprRetriever(WlpprRetrieverBase):
    """
        Classe permettant de récupérer les N derniers fonds d'écran
        parus sur le site
    """
    
    NB_ITEMS = 3
    FEED_URL = 'http://feeds.feedburner.com/wlppr'
    

    def retrieve(self):
        """
            Retourne les nb derniers fonds d'écran contenus dans le flux
            du site.
        """
        
        nb_left = self.NB_ITEMS
        feed_content = WlpprRetrieverBase.urlGetContents(FeedRecentWlpprRetriever.FEED_URL)
        
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


class RandomWlpprRetriever(WlpprRetrieverBase):
    """
        Classe permettant de récupérer un fond d'écran aléatoire
    """
    
    WLPPR_URL = 'http://wlppr.com/shuffle'
    WLPPR_TITLE_REGEX = '<h1><a href=".*">(.*)</a></h1>'
    WLPPR_LINKS_ZONE_REGEX = '<div id="downloads">(.*)</div>'
    WLPPR_LINKS_REGEX = '<a href="(.*?)">(.*?)</a>'
    
    
    def retrieve(self):
        """
            Récupère un fond d'écran aléatoire
        """
        
        page_content = WlpprRetrieverBase.urlGetContents(RandomWlpprRetriever.WLPPR_URL)
        
        # récupération du titre
        try:
            data_title = re.compile(RandomWlpprRetriever.WLPPR_TITLE_REGEX) \
                      .findall(page_content)[0]
        except IndexError:
            data_title = ''
        
        no, title = self.parseTitle(data_title)
        
        # récupération des différentes versions (tailles) du wlppr
        links_zone = re.compile(RandomWlpprRetriever.WLPPR_LINKS_ZONE_REGEX) \
                       .findall(page_content)[0]
        links = self.parseLinks(links_zone)
        
        if not len(links) == 0:
            self.wlpprs.append(Wlppr(no, title, links))
    
    def parseLinks(self, html):
        """ Récupère les liens des fonds d'écrans et leur taille """
        
        links = {}
        
        data_links = re.compile(RandomWlpprRetriever.WLPPR_LINKS_REGEX).findall(html)
        for url_part, size in data_links:
            links[size] = '%s%s' % (WlpprRetrieverBase.WLPPR_BASE_URL,
                                    url_part)
        
        return links
    
    def getText(self, element):
        return element.childNodes[0].nodeValue


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
    
    WlpprRetrieverBase.retrieveWlppr(url, path)
    
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
    (options, args) = parser.parse_args()

    # traitement des options
    Config.VERBOSE = options.verbose
    Config.WLPPR_TO_RETRIEVE = Config.RANDOM_WLPPR if options.mode == 'random' else \
                               Config.LATEST_WLPPR

    # lancement de la récupération du wlppr
    retriever = RandomWlpprRetriever() \
                if Config.WLPPR_TO_RETRIEVE is Config.RANDOM_WLPPR else \
                FeedRecentWlpprRetriever()
    
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
    else:
        chat('[-] Changement du fond d\'écran ...')
        
        setWallpaper(url)
    
        chat('[+] Fond d\'écran mis en place !')


if __name__ == '__main__':
	main()
