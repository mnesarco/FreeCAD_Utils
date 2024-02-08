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

from freecad.mnesarco.utils.extension import DocumentObject, DocumentObjectGui, find_python_objects_by_class, show_task_panel, close_task_panel
from freecad.mnesarco import App
from freecad.mnesarco.gui import Gui
from freecad.mnesarco.utils.toolbars import add_global_action
from freecad.mnesarco.resources import Icons, get_ui, tr
from freecad.mnesarco.utils.qt import BasicListItem, Qt, BasicQIcon
from freecad.mnesarco.utils.graphics import active_view


class PointOfViewObjectGui(DocumentObjectGui):

    Icon = Icons.camera

    def __init__(self, vobj):
        super(PointOfViewObjectGui, self).__init__(vobj)

    def setEdit(self, vobj, mode=0):
        view = active_view()
        if view:
            view.setCamera(self.Object.Proxy.Camera)
            show_task_panel(Form(vobj.Object.Name))

    def unsetEdit(self, vobj, mode=0):
        close_task_panel()

    def doubleClicked(self, vobj):
        self.setEdit(vobj, 0)


class PointOfViewObject(DocumentObject):

    Persist = [('Camera', None)]

    def __init__(self, obj):
        super(PointOfViewObject, self).__init__(obj)
        self.Camera = None
        view = active_view()
        if view:
            self.Camera = view.getCamera()


class Form:

    def __init__(self, current_name = None):

        form = Gui.PySideUic.loadUi(get_ui('camera', 'PointsOfViewPanel.ui'))
        form.setWindowTitle(tr("Saved Points of View"))
        self.form = form
        
        items = form.listWidget
        current = None
        for pov in find_python_objects_by_class(PointOfViewObject):
            item = BasicListItem(pov.Label, Icons.camera, data=pov.Name, editable=True)
            items.addItem(item)    
            if pov.Name == current_name:
                current = item
        items.itemSelectionChanged.connect(self.item_selection_changed)
        items.itemChanged.connect(self.update)
        if current:
            items.setCurrentItem(current)

        save = form.saveCamera
        save.setIcon(BasicQIcon(Icons.save_camera))
        save.clicked.connect(self.save)

        add = form.addCamera
        add.setIcon(BasicQIcon(Icons.add_camera))
        add.clicked.connect(self.add)


    def item_selection_changed(self):
        item = self.form.listWidget.currentItem()
        if item:
            obj = App.ActiveDocument.getObject(item.data(Qt.UserRole))
            Gui.ActiveDocument.ActiveView.setCamera(obj.Proxy.Camera)
        self.form.saveCamera.setEnabled(bool(self.form.listWidget.selectedItems()))

    def save(self, *args):
        item = self.form.listWidget.currentItem()
        if item:
            obj = App.ActiveDocument.getObject(item.data(Qt.UserRole))
            obj.Proxy.Camera = Gui.ActiveDocument.ActiveView.getCamera()

    def update(self, item):
        obj = App.ActiveDocument.getObject(item.data(Qt.UserRole))
        obj.Label = item.text()

    def add(self, *args):
        pov = self.create()
        item = BasicListItem(pov.Label, Icons.camera, data=pov.Name, editable=True)
        self.form.listWidget.addItem(item)            

    def refresh(self):
        items = self.form.listWidget
        for pov in find_python_objects_by_class(PointOfViewObject):
            if not self.find_by_data(pov.Name):
                item = BasicListItem(pov.Label, Icons.camera, data=pov.Name, editable=True)
                items.addItem(item)    

    def find_by_data(self, data):
        items = self.form.listWidget
        for i in range(items.count()):
            item = items.item(i)
            if item.data(Qt.UserRole) == data:
                return item

    def create(self):
        if not App.ActiveDocument:
            App.newDocument()

        group = DocumentObject.create_group('GroupPointsOfView', tr("Points of view [mnu]"), unique=True)       
        obj = DocumentObject.create('Camera', PointOfViewObject, PointOfViewObjectGui)
        obj.Proxy.move_to_group(group)

        return obj


def show():
    if active_view():
        show_task_panel(Form())


def init_gui_pov():
    add_global_action(
        name="CreatePointOfView",
        icon=Icons.camera,
        action=show,
        menu=tr("Points of View (Cameras)"),
        accel="Shift+Ctrl+V",
        activation=True)
