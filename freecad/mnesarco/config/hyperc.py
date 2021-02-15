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

from freecad.mnesarco.utils.qt import QtCore
from freecad.mnesarco import Gui
from freecad.mnesarco.resources import get_ui, tr
from freecad.mnesarco.utils import preferences as pref
from freecad.mnesarco.utils import validation


class HyperControllerConfig(QtCore.QObject):

    changed = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super(HyperControllerConfig, self).__init__(*args, **kwargs)
        self.form = Gui.PySideUic.loadUi(get_ui('config', 'hyperc.ui'))
        self.retranslateUi()
        self.refresh()
        self.form.port_input.textChanged.connect(self.changed)
        self.form.baud_input.textChanged.connect(self.changed)


    def retranslateUi(self):
        self.title = tr("Hyper Controller")
        self.form.label_banner.setText(tr("8+ DOF Hyper Controller"))
        self.form.label_port.setText(tr("Port name:"))       
        self.form.label_baud.setText(tr("Baud rate:"))

    def refresh(self):
        port = pref.get_mnesarco_pref("HyperController", "Port", default="/dev/ttyACM0")
        baud = pref.get_mnesarco_pref("HyperController", "BaudRate", default="115200")
        self.form.port_input.setText(port)
        self.form.baud_input.setText(baud)

    def validate(self):
        messages = []
        if not validation.validate_int(self.form.baud_input.text(), 9600, None, messages):
            self.message = tr('Baud rate: {}').format(messages[0])
            return False
        if not validation.validate_required(self.form.baud_input.text(), messages):
            self.message = tr('Baud rate: {}').format(messages[0])
            return False
        if not validation.validate_required(self.form.port_input.text(), messages):
            self.message = tr('Port name: {}').format(messages[0])
            return False

        return True

    def save(self):
        pref.set_mnesarco_pref("HyperController", "Port", self.form.port_input.text())
        pref.set_mnesarco_pref("HyperController", "BaudRate", self.form.baud_input.text())

