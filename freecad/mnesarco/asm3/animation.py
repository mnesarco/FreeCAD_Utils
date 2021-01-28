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

from freecad.mnesarco import App, Gui
from freecad.mnesarco.resources import tr

import time

class Asm3AnimationController:


    def __init__(self, assembly, animation, frames = 10):
        self.assembly = App.ActiveDocument.getObject(assembly)
        if not self.assembly:
            raise RuntimeError("Invalid Assembly (not found): {}".format(assembly))
        if frames <= 1:
            raise RuntimeError("Animation requires more than one frame")
        self.animation = animation
        self.frames = frames
        self.build()


    def build(self):
        if hasattr(self.animation, 'prepare'):
            self.animation.prepare()
        try:
            Gui.Selection.addSelection(self.assembly)
            parts = [(p, []) for p in self.assembly.Proxy.getPartGroup().Group]
            progress = App.Base.ProgressIndicator()
            progress.start(tr("Preprocessing..."), self.frames)
            for i in range(0, self.frames):
                self.animation.run(i)
                Gui.runCommand('asm3CmdQuickSolve', 0)
                for part in parts:
                    part[1].append(part[0].Placement)
                progress.next(True)
        finally:
            if hasattr(self.assembly, 'cleaunp'):
                self.assembly.cleanup()
            self.parts = parts


    def frame(self, frame):
        for part in self.parts:
            part[0].Placement = part[1][frame % self.frames]


    def animate(self, fps=20):
        try:
            Gui.runCommand('asm3CmdAutoRecompute', 0)
            waitime = 1.0/fps
            progress = App.Base.ProgressIndicator()
            progress.start(tr("Animating..."), self.frames)
            for i in range(0, self.frames):
                self.frame(i)
                progress.next(True)
                time.sleep(waitime)
        finally:
            Gui.runCommand('asm3CmdAutoRecompute', 1)

