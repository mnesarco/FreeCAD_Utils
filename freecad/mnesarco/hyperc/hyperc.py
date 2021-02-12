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

from freecad.mnesarco.utils.toolbars import add_global_action
from freecad.mnesarco.resources import Icons, tr
from freecad.mnesarco.hyperc import controller
from freecad.mnesarco import App
from freecad.mnesarco.utils.extension import log

def init_hyperc():

    try:
        import serial
        serial_available = True
    except ImportError:
        serial_available = False
        log(tr("8D Hyper Controller is disabled because the python module 'pyserial' was not found."))


    if serial_available:
        add_global_action(
            name="ToggleHyperController",
            icon=Icons.hyperc,
            action=lambda: controller.toggle(),
            menu=tr("Activate/Deactivate 8D Hyper Controller"),
            activation=lambda: App.ActiveDocument
        )

__all__ = ('init_hyperc')
