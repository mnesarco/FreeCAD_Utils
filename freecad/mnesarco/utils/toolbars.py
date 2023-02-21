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

from freecad.mnesarco.utils import preferences
from freecad.mnesarco.gui import Gui

TOOLBAR_NAME = "Mnesarco Utils"


__all__ = ('Command', 'add_global_action')


class Command:
    
    def __init__(self, icon, menu, action, accel=None, tooltip=None, activation=True, statustip=None):
        self.icon = icon
        self.accel = accel
        self.menu = menu
        self.tooltip = tooltip or menu
        self.activation = activation
        self.statustip = statustip
        self.action = action

    def GetResources(self):
        return {
            'Pixmap': self.icon,
            'Accel': self.accel,
            'MenuText': self.menu,
            'ToolTip': self.tooltip,
            'StatusTip': self.statustip or self.tooltip
        }

    def Activated(self):
        self.action()

    def isActive(self):
        if callable(self.activation):
            return self.activation()
        else:
            return self.activation


def _get_toolbar_key():
    toolbar_key = preferences.get_user_pref(preferences.PLUGIN_KEY, "ToolbarKey", root="Plugins")
    if toolbar_key:
        return "Workbench/Global/Toolbar/" + toolbar_key
    else:
        toolbar_key = preferences.get_user_pref_next_key("Workbench/Global/Toolbar", "Custom_")
        preferences.set_user_pref(preferences.PLUGIN_KEY, "ToolbarKey", toolbar_key, root="Plugins")
        return "Workbench/Global/Toolbar/" + toolbar_key


def add_global_action(name=None, icon=None, action=None, accel="", statustip=None, tooltip=None, whatsthis=None, menu=None, activation=True):

    # Register command
    cmd = Command(icon=str(icon), action=action, accel=accel, menu=menu, tooltip=tooltip or menu, activation=activation, statustip=statustip or menu)
    cmd_id = "Mnesarco_" + name.capitalize()
    Gui.addCommand(cmd_id, cmd)
    preferences.set_user_pref("Preferences/Commands", cmd_id, "Global")

    # Add Toolbar action
    toolbar_key = _get_toolbar_key()
    preferences.set_user_pref(toolbar_key, "Name", TOOLBAR_NAME)
    preferences.set_user_pref(toolbar_key, "Active", True)
    preferences.set_user_pref(toolbar_key, cmd_id, "FreeCAD")
    is_toolbar_configured = preferences.get_user_pref("MainWindow/Toolbars", TOOLBAR_NAME, kind=bool, default='UNSET')
    if is_toolbar_configured == 'UNSET':
        preferences.set_user_pref("MainWindow/Toolbars", TOOLBAR_NAME, True)
