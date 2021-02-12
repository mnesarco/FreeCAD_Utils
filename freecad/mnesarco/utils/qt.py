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

from PySide import QtGui, QtCore
from freecad.mnesarco.resources import Icons
import re
import tempfile
from pathlib import Path
import hashlib

Qt = QtCore.Qt

PIXMAP_PATTERN = re.compile(r'"([^"]*)"')

def BasicQIcon(path):
    qicon = QtGui.QIcon()
    qicon.addPixmap(QtGui.QPixmap(str(path)), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    return qicon


def BasicListItem(text, icon=None, data=None, editable=False):
    qicon = BasicQIcon(icon or Icons.generic)
    item = QtGui.QListWidgetItem(qicon, text)
    item.setData(Qt.UserRole, str(data))
    if editable:
        item.setFlags(item.flags() | Qt.ItemIsEditable)
    return item


def pixmap_to_png(xpm):
    name = '{0}.png'.format(hashlib.md5(xpm.encode()).hexdigest())
    tmp = Path(tempfile.gettempdir()).joinpath(name)
    if tmp.exists():
        return str(tmp)
    else:
        tmp = str(tmp)
        data = PIXMAP_PATTERN.findall(xpm)
        pixmap = QtGui.QPixmap(data)
        pixmap.save(tmp, 'PNG')
        return tmp


def extract_action_pixmap(action, size):
    name = '{0}.png'.format(action.objectName())
    tmp = Path(tempfile.gettempdir()).joinpath(name)
    if tmp.exists():
        return str(tmp)
    else:
        tmp = str(tmp)
        try:
            pixmap = action.icon().pixmap(size)
            pixmap.save(tmp, 'PNG')
            return tmp
        except BaseException:
            return None

class SignalObject(QtCore.QObject):

    activate = QtCore.Signal(tuple)

    def __init__(self, *args, **kwargs):
        super(SignalObject, self).__init__(*args, **kwargs)

    def forward(self, target):
        self.activate.connect(target)

    def trigger(self, *args):
        self.activate.emit(tuple(args))
