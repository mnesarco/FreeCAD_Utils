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

from freecad.mnesarco.config import platform, dialog, hyperc, remote


# +----------------------------------------------+
# | Pages API:                                   |
# |                                              |
# | class PageX(QtCore.QObject):                 |
# |   changed = QtCore.Signal()                  |
# |   def __init__(self, parent):                |
# |     super(PageX, self).__init__(parent)      |
# |     self.form = ...                          |
# |     self.title = ...                         |
# |   def validate(self) -> bool                 |
# |   def save(self)                             |
# +----------------------------------------------+
# | Then add_page(PageX(self)) in setup          +
# +----------------------------------------------+


class ConfigDialog(dialog.ConfigDialog):

    def __init__(self, parent=None):
        super(ConfigDialog, self).__init__(parent)

    def setup(self):        
        self.add_page(remote.RemoteConfig(self))
        # self.add_page(hyperc.HyperControllerConfig(self))
        self.add_page(platform.PlatformConfig(self))
