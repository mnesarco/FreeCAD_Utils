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
from pivy import coin
from math import radians


class private:
    camera = None


def get_bounding_box(objects, include_all=False):
    """Calculate the combined bounding box of objects"""

    bbox = None
    for obj in objects:    
        if obj.ViewObject.Visibility or include_all:    
            obbox = None
            if hasattr(obj, 'Shape'):
                obbox = obj.Shape.BoundBox
            elif hasattr(obj, 'Mesh'):
                obbox = obj.Mesh.BoundBox
            elif hasattr(obj, 'Points'):
                obbox = obj.Points.BoundBox
            if obbox:
                if bbox:
                    bbox = bbox.united(obbox)
                else:
                    bbox = obbox
    return bbox


def active_view():
    if Gui.ActiveDocument and Gui.ActiveDocument.ActiveView:
        return Gui.ActiveDocument.ActiveView
    return None


def get_camera():
    if active_view():
        if private.camera and private.camera.is_active():
            return private.camera
        else:
            private.camera = Camera()
            return private.camera
    return None


class Camera:

    X = 0
    Y = 1
    Z = 2

    def __init__(self):
        self.node = active_view().getCameraNode()
        self.current = 0        
        self._update_center()
        self.view = self.node.orientation.getValue()
        self.pos = self.node.position.getValue()
        self._config_direction(0)
        self.selection_pnt = self.center
        Gui.Selection.addObserver(self)

    def is_active(self):
        return self.node == Gui.ActiveDocument.ActiveView.getCameraNode()

    def _config_direction(self, i):
        # Evaluate the vectors corresponding to the three directions for the
        # current view, and assign the i-th one to self.direction.
        self.view = self.node.orientation.getValue()
        self.view = coin.SbRotation(self.view.getValue())
        self.pos = self.node.position.getValue()
        self.pos = coin.SbVec3f(self.pos.getValue())

        up = coin.SbVec3f(0,1,0)
        self.up = self.view.multVec(up)
        out = coin.SbVec3f(0,0,1)
        self.out = self.view.multVec(out)
        u = self.up.getValue()
        o = self.out.getValue()
        r = (u[1]*o[2]-u[2]*o[1], u[2]*o[0]-u[0]*o[2], u[0]*o[1]-u[1]*o[0])
        self.right = coin.SbVec3f(r)

        self.direction = [self.right, self.up, self.out][i]

    def rotate(self, i, value):
        if i != self.current:
            self._config_direction(i)
            self.current = i
        val = radians(value)
        rot = coin.SbRotation(self.direction, -val)
        nrot = self.view*rot
        prot = self.center
        self.node.orientation = nrot
        self.node.position = prot
           
    def zoom_in(self):
        active_view().zoomIn()

    def zoom_out(self):
        active_view().zoomOut()

    def pan(self, i, value):

        view = active_view()
        viewer = view.getViewer()
        vp = viewer.getSoRenderManager().getViewportRegion()
        cam = self.node
        ratio = vp.getViewportAspectRatio()
        vv = cam.getViewVolume(ratio)
        panplane = vv.getPlane(cam.focalDistance.getValue())

        if ratio < 1.0:
            vv.scale(1.0 / ratio)

        delta = [0.0, 0.0]
        delta[i] = float(value)/100.0
        delta = coin.SbVec2f(*delta)

        prevpos = coin.SbVec2f(0.0, 0.0)
        currpos = prevpos + delta

        line = vv.projectPointToLine(currpos)
        current_planept = panplane.intersect(coin.SbLine(*line))
        
        line = vv.projectPointToLine(prevpos)
        old_planept = panplane.intersect(coin.SbLine(*line))

        # Reposition camera according to the vector difference between the
        # projected points.
        cam.position = cam.position.getValue() - (current_planept - old_planept)


    def __del__(self):
        Gui.Selection.removeObserver(self)

    def _update_center(self, pnt=None):
        if pnt:
            self.center = App.Vector(*pnt)
        else:
            bbox = get_bounding_box(Gui.Selection.getSelection())
            if not bbox:
                bbox = get_bounding_box(App.ActiveDocument.Objects)
            if bbox:
                self.center = coin.SbVec3f(bbox.Center)
            else:
                self.center = coin.SbVec3f(0.0, 0.0, 0.0)

    def update_selection(self, pnt=None):
        if pnt:
            self.selection_pnt = pnt
        else:
            bbox = get_bounding_box(Gui.Selection.getSelection())
            if not bbox:
                bbox = get_bounding_box(App.ActiveDocument.Objects)
            if bbox:
                self.selection_pnt = bbox.Center
            else:
                self.selection_pnt = (0.0, 0.0, 0.0)

    def center_on_selection(self):
        if self.selection_pnt:
            self._update_center(self.selection_pnt)
            self._config_direction(self.current)
            self.rotate(self.current, 0)

    # SelectionObserver interface

    def addSelection(self, doc, obj, sub, pnt):
        if doc == App.ActiveDocument.Name:
            self.update_selection(pnt)

    def removeSelection(self, doc, obj, sub):
        if doc == App.ActiveDocument.Name:
            self.update_selection()

    def setSelection(self, doc):
        if doc == App.ActiveDocument.Name:
            self.update_selection()

    def clearSelection(self, doc):
        if doc == App.ActiveDocument.Name:
            self.update_selection()

