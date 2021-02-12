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
from freecad.mnesarco import Gui, App
from freecad.mnesarco.resources import get_ui, tr


class CreatePanel:

    VALID_NAME = re.compile(r'[a-zA-Z]\w+')

    def __init__(self, builder):
        self.form = Gui.PySideUic.loadUi(get_ui('timers', 'CreatePanel.ui'))
        self.form.setWindowTitle(tr('Create Timer'))
        self.form.label.setText(tr('Name:'))
        self.form.label_descr.setText(tr('The name will be used in expressions, it must be unique and cannot be changed later.'))
        self.form.errorMessage.setVisible(False)
        self.builder = builder

    def accept(self):
        self.form.errorMessage.setVisible(False)
        name = self.form.nameInput.text()
        if name and CreatePanel.VALID_NAME.match(name):
            if not App.ActiveDocument:
                App.newDocument()
            if not App.ActiveDocument.getObject(name):
                Gui.Control.closeDialog()
                self.create(name)
            else:
                self.form.errorMessage.setVisible(True)
                self.form.errorMessage.setText(tr("Duplicated name is not valid"))
        else:
            self.form.errorMessage.setVisible(True)
            self.form.errorMessage.setText(tr("Invalid name"))

    def create(self, name):
        self.builder(name)

