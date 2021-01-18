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

# +-------------------------------------------------------------------+
# | Data Record Format                                                |
# |                                                                   |
# | <int event> TAB <int|string value> NEW_LINE                       |
# +-------------------------------------------------------------------+

class Packet:

    # Axes events
    X   =  1 # X Orthogonal
    Y   =  2 # Y Orthogonal
    Z   =  3 # Z Orthogonal
    W   =  4 # W custom axis
    RX  =  5 # RX Rotational
    RY  =  6 # RY Rotational
    RZ  =  7 # RZ Rotational
    RW  =  8 # C custom axis
    XY0 =  9 # Center of XY Joystick
    ZW0 = 10 # Center of ZW Joystick

    # Button Events
    BUTTON_XY_CLICK        = 50
    BUTTON_XY_LONG_PRESS   = 51
    BUTTON_ZW_CLICK        = 60
    BUTTON_ZW_LONG_PRESS   = 61
    BUTTON_A_CLICK         = 70
    BUTTON_A_LONG_PRESS    = 71
    BUTTON_B_CLICK         = 80
    BUTTON_B_LONG_PRESS    = 81
    BUTTON_C_CLICK         = 90
    BUTTON_C_LONG_PRESS    = 91

    # Knob events
    KNOB                   = 100

    # Other events
    COMMENT                = 999

    __slots__ = ('event', 'data')

    def __init__(self, line):
        self.event = Packet.COMMENT
        self.data = 'Idle'
        if line:
            data = line.decode().rstrip().split('\t')
            self.event = int(data[0])
            if data[0] == Packet.COMMENT:
                self.data = " ".join(data[1:])
            else:
                self.data = int(data[1])
