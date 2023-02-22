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
from freecad.mnesarco.utils.extension import log_err
from freecad.mnesarco.resources import tr

PLUGIN_KEY = 'MnesarcoUtils'

def get_user_pref_keys(*path, root="BaseApp"):
    group_key = "User parameter:" + root + "/" + "/".join(path[:-1])
    key = path[-1]
    keys = App.ParamGet(group_key).GetStrings(key) or []
    return keys + [k for k in App.ParamGet(group_key).GetGroups() if k.startswith(key)]


def get_user_pref_last_key(*path, root="BaseApp"):
    key = path[-1]
    l = len(key)
    keys = get_user_pref_keys(*path, root=root)
    if keys:
        return max(int(k[l:]) for k in keys)
    else:
        return 0


def get_user_pref_next_key(*path, root="BaseApp"):
    key = path[-1]
    return key + str(get_user_pref_last_key(*path, root=root)+1)


def get_user_pref(*path, kind=str, default=None, root="BaseApp"):
    group_key = "User parameter:" + root + "/" + "/".join(path[:-1])
    key = path[-1]
    group = App.ParamGet(group_key)
    try:
        if kind == bool:
            v = group.GetBool(key)
            return default if v is None else v
        elif kind == int:
            return group.GetInt(key) or default
        elif kind == float:
            return group.GetFloat(key) or default
        elif kind == str:
            return group.GetString(key) or default
    except BaseException:
        pass
    return default


def set_user_pref(*path, root="BaseApp"):
    group_key = "User parameter:" + root + "/" + "/".join(path[:-2])
    key = path[-2]
    value = path[-1]
    kind = type(value)
    group = App.ParamGet(group_key)
    if kind == bool:
        group.SetBool(key, value)
    elif kind == int:
        group.SetInt(key, value)
    elif kind == float:
        group.SetFloat(key, value)
    elif kind == str:
        group.SetString(key, value)
    else:
        log_err(tr("Error writing {} of type {}").format(key, str(kind)))


def get_mnesarco_pref(*path, kind=str, default=None):
    return get_user_pref(PLUGIN_KEY, *path, kind=kind, default=default, root="Plugins")


def set_mnesarco_pref(*path):
    return set_user_pref(PLUGIN_KEY, *path, root="Plugins")


def clear_mnesarco_pref(*path):
    group_key = "User parameter:Plugins/" + PLUGIN_KEY + "/" + "/".join(path)
    group = App.ParamGet(group_key)
    group.Clear()
