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

import threading
from freecad.mnesarco import App
from freecad.mnesarco.gui import Gui
from freecad.mnesarco.utils.qt import QtCore
from freecad.mnesarco.utils.graphics import get_camera, Camera
from freecad.mnesarco.utils.extension import def_log
from freecad.mnesarco.hyperc.driver import Driver, Packet

# Logging config
TAG = "HyperController"
log = def_log(TAG)


class private:
    x_angle = 0.0
    y_angle = 0.0
    z_angle = 0.0


class HyperController(QtCore.QObject):

    event = QtCore.Signal(Packet)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.driver = Driver(**kwargs)
        self.thread = threading.Thread(target=self.event_loop, daemon=True)

    def event_loop(self):
        for packet in self.driver.packets():
            if packet and packet.event == Packet.COMMENT:
                log(packet.data)
            else:
                self.event.emit(packet)

    def start(self):
        self.thread.start()

    def stop(self):
        self.driver.close()


QtCore.Slot(Packet)
def event_handler(packet):
    camera = get_camera()
    if camera:
        d =  packet.data

        # Rotations

        if packet.event == Packet.RX:       
            private.x_angle += d
            private.y_angle = 0
            private.z_angle = 0
            camera.rotate(Camera.X, private.x_angle)
        
        elif packet.event == Packet.RY:       
            private.y_angle += d
            private.x_angle = 0
            private.z_angle = 0
            camera.rotate(Camera.Y, private.y_angle)
        
        elif packet.event == Packet.RZ:       
            private.z_angle += d
            private.y_angle = 0
            private.x_angle = 0
            camera.rotate(Camera.Z, private.z_angle)

        # Zoom

        elif packet.event == Packet.W:
            if d > 0:
                camera.zoom_in()
            else:
                camera.zoom_out()

        # Panning

        elif packet.event == Packet.Y:
            camera.pan(Camera.X, d)

        elif packet.event == Packet.X:
            camera.pan(Camera.Y, d)

        # Transparency

        elif packet.event == Packet.Z:
            for obj in Gui.Selection.getSelection():
                part = App.ActiveDocument.getObject(obj.Name)
                if hasattr(part, 'Transparency'):
                    part.Transparency += d
                elif hasattr(part, 'ViewObject') and hasattr(part.ViewObject, 'Transparency'):
                    part.ViewObject.Transparency += d

        # Button B

        elif packet.event == Packet.BUTTON_B_CLICK:
            camera.center_on_selection()
            

def start():
    stop()
    App.Mnesarco_HyperC = HyperController()
    App.Mnesarco_HyperC.event.connect(event_handler)
    App.Mnesarco_HyperC.start()


def stop():
    if hasattr(App, 'Mnesarco_HyperC'):
        try:
            App.Mnesarco_HyperC.stop()
        except Exception:
            pass
        delattr(App, 'Mnesarco_HyperC')


def toggle():
    if hasattr(App, 'Mnesarco_HyperC'):
        stop()
    else:
        start()


__all__ = ('start', 'stop', 'toggle')
