# -*- coding: utf-8 -*-
# 
# Copyright (C) 2021 Frank David Martinez M. <https://github.com/mnesarco/>
# 
# This file is part of Utils.
# 
# Utils is free software: you can redistribute it and/or modify
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

import sys
import freecad.mnesarco.utils.preferences as pref
from freecad.mnesarco.utils.extension import log
from freecad.mnesarco.resources import tr


def add_python_path(path):
    sys.path.insert(0, path)


def add_additional_python_paths():
    keys = pref.get_user_pref_keys(pref.PLUGIN_KEY, "Platform", "PythonPath", "Path", root="Plugins")
    if keys:
        for key in keys:
            path = pref.get_mnesarco_pref("Platform", "PythonPath", key)
            log(tr("[Python Path] Adding {}").format(path))
            add_python_path(path)


def init_platform():
    add_additional_python_paths()
