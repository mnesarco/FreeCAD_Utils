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

from freecad.mnesarco.utils.toolbars import add_global_action
from freecad.mnesarco.resources import Icons, tr
from freecad.mnesarco import App

def start():
    from freecad.mnesarco.remote.server import start_remote_server
    start_remote_server()


def init_remote():

    add_global_action(
        name="Remote",
        icon=Icons.remote,
        action=start,
        menu=tr("Start Remote Control Server"),
        activation=lambda: App.ActiveDocument
    )

__all__ = ('init_remote')
