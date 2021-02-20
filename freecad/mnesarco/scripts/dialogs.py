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
from freecad.mnesarco import App
from freecad.mnesarco.gui import Gui
from freecad.mnesarco.resources import get_ui, tr, get_template
from freecad.mnesarco.utils.extension import show_task_panel
from freecad.mnesarco.utils.editor import CodeEditorPanel
from freecad.mnesarco.utils.files import resolve_path
from freecad.mnesarco.utils.dialogs import error_dialog


class CreatePanel:

    VALID_NAME = re.compile(r'[a-zA-Z]\w+')

    def __init__(self, builder):
        self.form = Gui.PySideUic.loadUi(get_ui('scripts', 'CreatePanel.ui'))
        self.form.setWindowTitle(tr('Create Script'))
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
                if App.ActiveDocument.FileName:
                    Gui.Control.closeDialog()
                    self.create(name)
                else:
                    self.form.errorMessage.setVisible(True)
                    self.form.errorMessage.setText(tr("The Actvive Document must be saved before adding scripts"))
            else:
                self.form.errorMessage.setVisible(True)
                self.form.errorMessage.setText(tr("Duplicated name is not valid"))
        else:
            self.form.errorMessage.setVisible(True)
            self.form.errorMessage.setText(tr("Invalid name"))

    def create(self, name):
        obj = self.builder(name)
        file = resolve_path(name + ".py", App.ActiveDocument.FileName)
        if not file.exists():
            try:
                file.write_text(get_template("scripts", "default_script.py.txt"))
            except BaseException:
                error_dialog(tr("Script file '{}' cannot be created").format(str(file)), raise_exception=True)
                return
        show_task_panel(CodeEditorPanel(obj.Name, file))

