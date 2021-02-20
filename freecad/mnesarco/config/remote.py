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

import re
from freecad.mnesarco.utils.qt import QtCore
from freecad.mnesarco.gui import Gui
from freecad.mnesarco.resources import get_ui, tr
from freecad.mnesarco.utils import preferences as pref
from freecad.mnesarco.utils import networking
from freecad.mnesarco.utils import validation


class RemoteConfig(QtCore.QObject):

    changed = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super(RemoteConfig, self).__init__(*args, **kwargs)
        self.form = Gui.PySideUic.loadUi(get_ui('config', 'remote.ui'))
        self.retranslateUi()
        self.refresh()
        self.form.port_input.textChanged.connect(self.changed)

    def retranslateUi(self):
        self.title = tr("Remote")
        self.form.label_banner.setText(tr("Remote Control ({})".format(networking.get_local_ip())))
        self.form.label_port.setText(tr("Port number:"))       

    def refresh(self):
        port = str(pref.get_mnesarco_pref("Remote", "Port", default=8521))
        self.form.port_input.setText(port)

    def validate(self):
        messages = []
        if not validation.validate_int(self.form.port_input.text(), 1000, None, messages):
            self.message = tr('Port number: {}').format(messages[0])
            return False
        if not validation.validate_required(self.form.port_input.text(), messages):
            self.message = tr('Port number: {}').format(messages[0])
            return False
        return True

    def save(self):
        pref.set_mnesarco_pref("Remote", "Port", int(self.form.port_input.text()))

