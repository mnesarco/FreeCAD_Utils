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

import hashlib
from pathlib import Path

# Mapping from hashes to file paths
allowed_files = {}

# Mapping from hashes to macro file path
macro_files = {}

# Mapping from hashes to Workbench names
workbench_keys = {}

# Mapping from hashes to toolbar names
toolbar_keys = {}

# Mapping from hashes to action names
action_keys = {}

def export_file(path):
    key = '/' + hashlib.sha256(str(path).encode()).hexdigest()
    allowed_files[key] = str(path)
    return key


def export_macro(macro):
    macro_files[macro.key] = macro.file
    return macro.key


def export_workbench(wb):
    key = hashlib.sha256(str(wb.key).encode()).hexdigest()
    workbench_keys[key] = wb.key
    return key


def export_toolbar(toolbar):
    key = hashlib.sha256(str(toolbar).encode()).hexdigest()
    toolbar_keys[key] = toolbar
    return key


def export_action(toolbar, action):
    key = hashlib.sha256(str(toolbar + "." + action.objectName()).encode()).hexdigest()
    action_keys[key] = action
    return key


def get_exported_action(key):
    return action_keys.get(key, None)


def get_exported_file(key):
    return allowed_files.get(key, key)


def get_exported_wb(key):
    return workbench_keys.get(key, None)


def get_exported_toolbar(key):
    return toolbar_keys.get(key, None)


def get_exported_macro(key):
    path = macro_files.get(key, None)
    if path and Path(path).exists():
        return path

