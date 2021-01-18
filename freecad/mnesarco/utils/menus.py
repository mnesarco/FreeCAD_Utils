# -*- coding: utf-8 -*-
# 
# Copyright (C) 2021 Frank David Martinez M. <https://github.com/mnesarco/>
# 
# This file is part of Utils.
# 
# Utils is free software: you can redistribute it and/or modify
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

from freecad.mnesarco.utils.qt import QtGui
from freecad.mnesarco import Gui


def find_or_add(root, name):
    for menu in root.findChildren(QtGui.QMenu):
        if menu.title() == name:
            return menu   
    return root.addMenu(name)


def add_menu(path, text, icon, handle):
    
    window = Gui.getMainWindow()
    bar = window.menuBar()    
    menu = bar

    for name in path:
        menu = find_or_add(menu, name)
    
    for action in menu.actions():
        if action.text() == text:
            menu.removeAction(action)
            break
    
    action = QtGui.QAction(QtGui.QIcon(icon), text, window.menuBar())
    menu.addAction(action)
    action.triggered.connect(handle)
