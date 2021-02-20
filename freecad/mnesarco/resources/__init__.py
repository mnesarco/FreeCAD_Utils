# -*- coding: utf-8 -*-
# 
# Copyright (C) 2021 Frank David Martinez M. <https://github.com/mnesarco/>
# 
# This file is part of Mnesarco Utils.
# 
# Mnesarco Utils is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Utils is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Mnesarco Utils.  If not, see <http://www.gnu.org/licenses/>.
# 

import functools
from pathlib import Path
from freecad.mnesarco import App

resources_path = Path(__file__).parent
icons_path = resources_path.joinpath('icons')
ui_path = resources_path.joinpath('ui')
translations_path = resources_path.joinpath('translations')
templates_path = resources_path.joinpath('templates')

# +-------------------------------------------------------------+
# | Icons                                                       |
# +-------------------------------------------------------------+

class Icons:

    @classmethod
    def load(cls):
        for file in icons_path.glob('*.svg'):
            setattr(cls, file.stem, file) 

Icons.load()

# +-------------------------------------------------------------+
# | UI                                                          |
# +-------------------------------------------------------------+

def get_ui(*path):
    return str(ui_path.joinpath(*path))


# +-------------------------------------------------------------+
# | Templates                                                   |
# +-------------------------------------------------------------+

def get_template(*path):
    return templates_path.joinpath(*path).read_text()


# +-------------------------------------------------------------+
# | Translation                                                 |
# +-------------------------------------------------------------+

class TranslationSetup:

    status = 0
    encoding = None

    @staticmethod
    def setup_tr():
        from freecad.mnesarco.utils.qt import QtGui
        from freecad.mnesarco.gui import Gui
        try:
            Gui.addLanguagePath(str(translations_path))
            Gui.updateLocale()
            TranslationSetup.status = 1
            try:
                TranslationSetup.encoding = QtGui.QApplication.UnicodeUTF8
            except:
                TranslationSetup.encoding = None
        except Exception as ex:
            App.Console.PrintError('Translation loading error: ', str(ex))
            TranslationSetup.status = -1

    @staticmethod
    def init():
        if TranslationSetup.status == 0:
            TranslationSetup.setup_tr()
        return TranslationSetup.status > 0

    @staticmethod
    def tr(text):
        from freecad.mnesarco.utils.qt import QtGui
        if TranslationSetup.init():
            if TranslationSetup.encoding:
                return QtGui.QApplication.translate('mnesarco', text, None, TranslationSetup.encoding)
            else:
                return QtGui.QApplication.translate('mnesarco', text, None)
        else:
            return text


@functools.lru_cache()
def tr(text):
    """Translate text"""
    return TranslationSetup.tr(text) or text




