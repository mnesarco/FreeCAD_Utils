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

from freecad.mnesarco.utils.qt import QtGui, QtCore
from freecad.mnesarco.resources import tr


class ConfigDialog(QtGui.QDialog):


    def __init__(self, parent=None):
        super(ConfigDialog, self).__init__(parent)
        self.setObjectName("ConfigDialog")
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.resize(542, 505)
        self.layout = QtGui.QVBoxLayout(self)
        self.tabWidget = QtGui.QTabWidget(self)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.North)

        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Save | QtGui.QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)

        self.layout.addWidget(self.tabWidget)
        self.layout.addWidget(buttons)
        self.retranslateUi()
        self.dirty = False

        self.pages = []
        self.setup()
        self.tabWidget.setCurrentIndex(0)


    def retranslateUi(self):
        self.setWindowTitle(tr("Mnesarco Utils Config"))


    def add_page(self, page):
        page.changed.connect(self.changed)
        self.tabWidget.addTab(page.form, page.title)
        self.pages.append(page)


    def setup(self):
        """Abstract method to be implemented in subclasses"""
        pass


    def changed(self):
        self.dirty = True


    def save(self):
        if self.dirty:
            for i, page in enumerate(self.pages):
                if not page.validate():
                    self.tabWidget.setCurrentIndex(i)
                    return
            for page in self.pages:
                page.save()
            self.dirty = False
        self.accept()


    def confirm_discard(self):
        if self.dirty:
            dlg = QtGui.QMessageBox()
            dlg.setText(tr("Config has been modified."))
            dlg.setInformativeText(tr("Do you want to save your changes?"))
            dlg.setStandardButtons(QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard | QtGui.QMessageBox.Cancel)
            dlg.setDefaultButton(QtGui.QMessageBox.Save)
            ret = dlg.exec()
            if ret == QtGui.QMessageBox.Save:
                self.save()
            elif ret == QtGui.QMessageBox.Discard:
                self.reject()
            else:
                return False                
        else:
            self.reject()
        return True


    def closeEvent(self, event):
        if self.dirty and not self.confirm_discard():
            event.ignore()

