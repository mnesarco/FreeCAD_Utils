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

from freecad.mnesarco.utils.math import cmp

class DataSignal:

    RISING   = '/'
    STEADY    = '-'
    FALLING   = '\\'
    MONOTONIC = '.'

    __slots__ = ('value', 'sensitivity', 'rising', 'falling', 'steady', 'data')
    
    def __init__(self, sensitivity=0):
        self.value = (0.0, 0.0)
        self.sensitivity = sensitivity
        self.steady = lambda to: None
        self.rising = lambda mag, to: None
        self.falling = lambda mag, to: None
        self.data = lambda mag, d: None


    def dispatch(self, c):

        """Dispatch events: rising, falling, steady, data"""
        
        a, b = self.value
        
        mag = abs(c - b)
        if mag < self.sensitivity:
            b = c
            mag = 0

        old_dir, new_dir = cmp(b, a), cmp(c, b)
        self.value = b, c

        if old_dir != new_dir:
            if old_dir < 0 and new_dir > 0:
                self.rising(mag, c)
            elif new_dir < 0 and old_dir > 0:
                self.falling(mag, c)
            else:
                self.steady(c)

        if mag > 0:
            self.data(mag, c)
        

    def proc(self, c):

        """ Returns a tuple (Event, Magnitude, Point)"""
        
        a, b = self.value
        
        mag = abs(c - b)
        if mag < self.sensitivity:
            b = c
            mag = 0

        old_dir, new_dir = cmp(b, a), cmp(c, b)
        self.value = b, c

        if old_dir == new_dir and old_dir != 0:
            return DataSignal.MONOTONIC, mag * new_dir, c
        elif new_dir > 0:
            return DataSignal.RISING, mag, c
        elif new_dir < 0:
            return DataSignal.FALLING, mag, c
        else:
            return DataSignal.STEADY, mag, c


