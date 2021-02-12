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

from .wire import Packet
from freecad.mnesarco.utils.extension import def_log_err, def_log
from freecad.mnesarco.resources import tr
from freecad.mnesarco.utils import preferences as pref

# Logging config
TAG = "HyperController"
log_err = def_log_err(TAG)
log = def_log(TAG)


class Driver:

    PREF_KEY = "HyperController"
    DEFAULT_PORT_NAME = "/dev/ttyACM0"
    DEFAULT_BAUD_RATE = 115200
    DEFAULT_TIMEOUT = 0.1

    def __init__(self, port_name=None, timeout=None, baud_rate=None):
        self.port      = port_name or pref.get_mnesarco_pref(Driver.PREF_KEY, "Port", default=Driver.DEFAULT_PORT_NAME)
        self.baud_rate = baud_rate or pref.get_mnesarco_pref(Driver.PREF_KEY, "BaudRate", default=Driver.DEFAULT_BAUD_RATE)
        self.timeout   = timeout   or pref.get_mnesarco_pref(Driver.PREF_KEY, "Timeout", default=Driver.DEFAULT_TIMEOUT)
        try:
            self.is_open = False
            log(tr("Connecting to port {0} at {1}Bd with a timeout of {2}s").format(self.port, self.baud_rate, self.timeout))
            import serial
            self.stream = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
            self.is_open = True
        except ImportError:
            log_err(tr("pyserial module not found"))
        except Exception as e:
            log_err(str(e))

    def next_packet(self):
        if not self.is_open:
            raise RuntimeError('Port {} is closed'.format(self.port))
        try:
            line = self.stream.readline()
            if line:
                return Packet(line)
        except Exception:
            return None  # Ignore corrupt packets

    def close(self):
        if self.is_open:
            try:
                self.stream.close()
            except Exception:
                pass
        self.is_open = False

    def packets(self):
        while self.is_open:
            p = self.next_packet()
            if p:
                yield p


__all__ = ('Driver', 'Packet')
