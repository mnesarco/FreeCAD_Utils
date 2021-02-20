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

import sys, os

from freecad.mnesarco.utils.qt import QtCore
from freecad.mnesarco.gui import Gui
from freecad.mnesarco.resources import get_ui, tr
from freecad.mnesarco.utils import preferences as pref


class PlatformConfig(QtCore.QObject):

    changed = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super(PlatformConfig, self).__init__(*args, **kwargs)
        self.form = Gui.PySideUic.loadUi(get_ui('config', 'platform.ui'))
        self.retranslateUi()
        self.refresh()
        self.form.pathsInput.textChanged.connect(self.changed)


    def retranslateUi(self):
        self.title = tr("Platform")
        self.form.label.setText(tr("Additional python paths (one per line):"))
        self.form.labelSystemPaths.setText(tr("Core python paths:"))
        

    def refresh(self):
        additional = []
        keys = pref.get_user_pref_keys(pref.PLUGIN_KEY, "Platform", "PythonPath", "Path", root="Plugins")
        if keys:
            for key in keys:
                path = pref.get_mnesarco_pref("Platform", "PythonPath", key)
                additional.append(path)

        system = []
        for path in sys.path:
            if path not in additional:
                system.append(path)
        
        self.form.systemPaths.setText("\r\n".join(system))
        self.form.pathsInput.setPlainText("\r\n".join(additional))


    def validate(self):
        return True


    def save(self):
        pref.clear_mnesarco_pref("Platform", "PythonPath")
        additional = self.form.pathsInput.toPlainText().splitlines()
        i = 0
        added = set()
        for path in additional:
            path = path.strip()
            if path and path not in added and os.path.exists(path):
                pref.set_mnesarco_pref("Platform", "PythonPath", "Path{}".format(i), path)
                added.add(path)
                i += 1

