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

from freecad.mnesarco.gui import Gui
from freecad.mnesarco.scripts.hook import init_gui_scripts
from freecad.mnesarco.timers import init_gui_timers
from freecad.mnesarco.camera.pov import init_gui_pov
from freecad.mnesarco.utils.platform import init_platform
from freecad.mnesarco.hyperc import init_hyperc
from freecad.mnesarco.config import init_config
from freecad.mnesarco.remote import init_remote
from freecad.mnesarco.objects import init_objects

def bootstrap():
    init_platform()
    init_gui_scripts()
    init_gui_timers()
    init_gui_pov()
    init_hyperc()
    init_config()
    init_remote()
    init_objects()


def bootstrap_hook(wb):
    Gui.getMainWindow().workbenchActivated.disconnect(bootstrap_hook)
    bootstrap()


Gui.getMainWindow().workbenchActivated.connect(bootstrap_hook)

