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

from freecad.mnesarco.utils import qt
from freecad.mnesarco import Gui
from freecad.mnesarco.remote.exports import export_action
from freecad.mnesarco.remote import page
from freecad.mnesarco.resources import tr

excluded = ['NoneWorkbench', 'CompleteWorkbench', 'StartWorkbench']


class WorkbenchWrapper:

    def __init__(self, wb, key):
        self.wb = wb
        self.key = key

    def get_icon(self):
        if hasattr(self.wb, 'Icon'):
            icon = self.wb.Icon
            if icon:
                if icon.find('XPM') >= 0:
                    icon = qt.pixmap_to_png(icon)
            else:
                icon = "img/noicon.svg"
        else:    
            icon = "img/noicon.svg"
        return icon

    def get_text(self):
        if hasattr(self.wb, 'MenuText'):
            return self.wb.MenuText
        elif hasattr(self.wb, 'ToolTip'):
            return self.wb.ToolTip
        else:
            return None


class AllWorkbenchesPage(page.Page):

    def title(self):
        return tr("All Macros")

    def sections(self):
        actions = get_all_workbenches()
        return [page.Section(tr("All"), actions)]


class WorkbenchPage(page.Page):

    def __init__(self, key):
        self.key = key

    def title(self):
        return "TODO"

    def stylesheet(self):
        return "css/compact.css"

    def sections(self):
        self.wb = WorkbenchWrapper(Gui.listWorkbenches()[self.key], self.key)
        mw = Gui.getMainWindow()
        excluded = ['File', 'Workbench', 'Macro', 'View', 'Structure']
        sections = []
        for name in self.wb.wb.listToolbars():
            if name in excluded:
                continue            
            toolbar = mw.findChildren(qt.QtGui.QToolBar, name)
            actions = []
            for button in toolbar[0].findChildren(qt.QtGui.QToolButton):
                if button.text() == '': continue
                qaction = button.defaultAction()
                key = export_action(name, qaction)
                actions.append(page.Action(qaction.iconText(), qt.extract_action_pixmap(qaction, 64), '/action/{}'.format(key)))
            if actions:
                sections.append(page.Section(name, actions))
        return sections



def get_all_workbenches():
    workbenches = Gui.listWorkbenches()
    actions = []
    for key, wbc in workbenches.items():
        if key not in excluded:
            wb = WorkbenchWrapper(wbc, key)
            icon = wb.get_icon()
            text = wb.get_text() or key
            actions.append(page.Action(text, icon, '/workbench/{}'.format(wb.key)))
    return actions