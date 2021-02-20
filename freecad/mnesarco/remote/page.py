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

class Page:

    def title(self):
        return "Page"

    def sections(self):
        return []

    def stylesheet(self):
        return "css/default.css"

    def data(self):
        return {
            'title': self.title(),
            'stylesheet': self.stylesheet(),
            'sections': [s.data() for s in self.sections()]
        }

class Section:

    def __init__(self, title, actions):
        self.title = title
        self.actions = actions
    
    def data(self):
        return {
            'title': self.title,
            'actions': [s.data() for s in self.actions]
        }

class Action:
    
    def __init__(self, title, icon, action):
        self.title = title
        self.icon = icon
        self.action = action

    def data(self):
        return self.__dict__