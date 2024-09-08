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

from freecad.mnesarco import App
from freecad.mnesarco.utils import toolbars 
from freecad.mnesarco.resources import Icons, tr

def create():
    from .svg_file import SvgFile
    import FreeCADGui as Gui # type: ignore
    obj = SvgFile.create("SvgFile")
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(App.ActiveDocument.Name, obj.Name)


def init_svg():
    toolbars.add_global_action(
        name="CreateSvgFileObject",
        icon=Icons.svg,
        action=create,
        menu=tr("Create Svg File Object"),
        activation=lambda: App.ActiveDocument)
