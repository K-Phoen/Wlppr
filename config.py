#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       config.py
#
#       Fichier de configuration
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


class Config:
    """ Classe "conteneur" pour le stockage de la configuration """

    RANDOM_WLPPR    = 0x01
    LATEST_WLPPR    = 0x02
    

    WLPPR_TO_RETRIEVE = RANDOM_WLPPR
    # le wall téléchargé sera enregistré ici
    WLPPR_FILE = '~/.wlppr.jpg'
    # liste des tailles favorites (par ordre de préférences décroissantes)
    PREFERED_SIZES = ['1600x1200']

    VERBOSE = False