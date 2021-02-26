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
# Mnesarco Utils is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Mnesarco Utils.  If not, see <http://www.gnu.org/licenses/>.
# 

from freecad.mnesarco import App
from freecad.mnesarco.gui import Gui
from freecad.mnesarco.resources import get_ui, tr, Icons
from freecad.mnesarco.utils.qt import QtGui, QtCore
import re

Types = [
    ('Spreadsheet::Sheet', tr('Spreadsheet'), str(Icons.fc_create_spreadsheet), 'SpreadsheetWorkbench'),
    ('App::Part', tr('Part'), str(Icons.fc_create_part), 'PartWorkbench'),
    ('PartDesign::Body', tr('Part Body'), str(Icons.fc_create_body), 'PartDesignWorkbench'),
]

VALID_NAME = re.compile(r'[a-zA-Z]\w+')

class NamedObjectForm(QtCore.QObject):

    def __init__(self, *args, **kwargs):
        super(NamedObjectForm, self).__init__(Gui.getMainWindow())
        form = Gui.PySideUic.loadUi(get_ui('objects', 'NamedObject.ui'), self)
        form.setWindowModality(QtCore.Qt.ApplicationModal)
        self.dialog = form
        self.ui_retranslate()

        types = QtGui.QStandardItemModel(form.list_types)
        for type_id, name, icon, wb in Types:
            item = QtGui.QStandardItem(QtGui.QIcon(icon), name)
            item.setData(type_id)
            types.appendRow(item)
        self.types = types   
        form.list_types.setModel(types)
        form.list_types.setCurrentIndex(types.index(0,0))
        
        buttons = form.buttons
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        self.input = form.input_name
        form.show()

    def save(self):
        name = self.input.text()
        sel = self.dialog.list_types.currentIndex()
        if name and VALID_NAME.match(name) and sel:
            if not App.ActiveDocument:
                App.newDocument()
            typeid = Types[sel.row()][0]
            Gui.activateWorkbench(Types[sel.row()][3])
            App.ActiveDocument.addObject(typeid, name)
        else:
            self.input.setFocus()

    def reject(self):
        self.dialog.close()
        self.dialog.deleteLater()

    def ui_retranslate(self):
        self.dialog.setWindowTitle(tr("Add Named Object"))
        self.dialog.label_types.setText(tr('Types:'))
        self.dialog.label_name.setText(tr('Name:'))

    @staticmethod
    def create():
        return NamedObjectForm()