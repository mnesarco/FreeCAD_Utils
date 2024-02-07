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


from pivy import coin
from freecad.mnesarco import App
from freecad.mnesarco.utils.timers import execute_later


# +-------------------------------------------------------------+
# | PythonFeature                                               |
# +-------------------------------------------------------------+

class Property:

    Bool                = "App::PropertyBool"
    BoolList            = "App::PropertyBoolList"
    Float               = "App::PropertyFloat"
    FloatList           = "App::PropertyFloatList"
    FloatConstraint     = "App::PropertyFloatConstraint"
    Quantity            = "App::PropertyQuantity"
    QuantityConstraint  = "App::PropertyQuantityConstraint"
    Angle               = "App::PropertyAngle"
    Distance            = "App::PropertyDistance"
    Length              = "App::PropertyLength"
    Speed               = "App::PropertySpeed"
    Acceleration        = "App::PropertyAcceleration"
    Force               = "App::PropertyForce"
    Pressure            = "App::PropertyPressure"
    Integer             = "App::PropertyInteger"
    IntegerConstraint   = "App::PropertyIntegerConstraint"
    Percent             = "App::PropertyPercent"
    Enumeration         = "App::PropertyEnumeration"
    IntegerList         = "App::PropertyIntegerList"
    IntegerSet          = "App::PropertyIntegerSet"
    Map                 = "App::PropertyMap"
    String              = "App::PropertyString"
    UUID                = "App::PropertyUUID"
    Font                = "App::PropertyFont"
    StringList          = "App::PropertyStringList"
    Link                = "App::PropertyLink"
    LinkSub             = "App::PropertyLinkSub"
    LinkList            = "App::PropertyLinkList"
    LinkSubList         = "App::PropertyLinkSubList"
    Matrix              = "App::PropertyMatrix"
    Vector              = "App::PropertyVector"
    VectorList          = "App::PropertyVectorList"
    Placement           = "App::PropertyPlacement"
    PlacementLink       = "App::PropertyPlacementLink"
    PlacementList       = "App::PropertyPlacementList"
    Color               = "App::PropertyColor"
    ColorList           = "App::PropertyColorList"
    Material            = "App::PropertyMaterial"
    Path                = "App::PropertyPath"
    File                = "App::PropertyFile"
    FileIncluded        = "App::PropertyFileIncluded"
    PythonObject        = "App::PropertyPythonObject"
    PartShape           = "Part::PropertyPartShape"
    GeometryList        = "Part::PropertyGeometryList"
    ShapeHistory        = "Part::PropertyShapeHistory"
    FilletEdges         = "Part::PropertyFilletEdges"
    ConstraintList      = "Sketcher::PropertyConstraintList"

    Flag_Default        =  0  # No special property type
    Flag_ReadOnly       =  1  # Property is read-only in the editor
    Flag_Transient      =  2  # Property won't be saved to file
    Flag_Hidden         =  4  # Property won't appear in the editor
    Flag_Output         =  8  # Modified property doesn't touch its parent container
    Flag_NoRecompute    = 16  # Modified property doesn't touch its container for recompute    


def default_getstate(obj):
    fields = getattr(obj.__class__, 'Persist', [])
    state = dict(FCName=getattr(obj, 'FCName', None))
    for field, default in fields:
        state[field] = getattr(obj, field, default)
    return state


def default_setstate(obj, state):
    fields = getattr(obj.__class__, 'Persist', [])
    obj.Type = getattr(obj.__class__, 'Type', obj.__class__.__name__)
    obj.FCName = None
    if state:
        obj.FCName = state.get('FCName', None)
        for field, default in fields:
            setattr(obj, field, state.get(field, default))


class DocumentObject:

    def __init__(self, obj):
        self.Type = getattr(self.__class__, 'Type', self.__class__.__name__)
        self.FCName = obj.Name
        obj.Proxy = self

    def __getstate__(self):
        return default_getstate(self)

    def __setstate__(self, state):
        if isinstance(state, str):
            state = dict(Type=state)
        default_setstate(self, state)

    def get_object(self):
        return App.ActiveDocument.getObject(self.FCName)

    def onDocumentRestored(self, fp):
        self.FCName = fp.Name

    def move_to_group(self, group):
        obj = self.get_object()
        obj.adjustRelativeLinks(group)
        group.addObject(obj)

    @staticmethod
    def create(name, proxy, view_provider=None):
        obj = App.ActiveDocument.addObject('App::FeaturePython', name)
        proxy(obj)
        if App.GuiUp and view_provider:
            view_provider(obj.ViewObject)
        return obj

    @staticmethod
    def create_group(name, label=None, unique=False):
        group = App.activeDocument().getObject(name)
        if unique and group:
            return group
        else:
            group = App.activeDocument().addObject('App::DocumentObjectGroup', name)
            group.Label = label or name
            return group


class DocumentObjectGui:

    def __init__(self, vobj):
        vobj.Proxy = self
        self.Type = getattr(self.__class__, 'Type', self.__class__.__name__)

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object
        self.standard = coin.SoGroup()
        vobj.addDisplayMode(self.standard, "Standard")

    def getIcon(self):
        icon = getattr(self.__class__, 'Icon', None)
        if icon:
            return str(icon)
        else:
            return str(Icons.generic)

    def getDisplayModes(self, vobj):
        return ["Standard"]

    def getDefaultDisplayMode(self):
        return "Standard"

    def setDisplayMode(self, mode):
        return mode

    def __getstate__(self):
        return default_getstate(self)

    def __setstate__(self, state):
        if isinstance(state, str):
            state = dict(Type=state)
        default_setstate(self, state)


# +-------------------------------------------------------------+
# | Search                                                      |
# +-------------------------------------------------------------+

def find_python_objects_by_class(cls):
    if isinstance(cls, str):
        def accept(obj):
            return obj.Proxy.__class__.__name__ == cls
    else:
        def accept(obj):
            return isinstance(obj.Proxy, cls)
    if App.ActiveDocument:
        for obj in App.ActiveDocument.Objects:
            if obj.TypeId == 'App::FeaturePython' and accept(obj):
                yield obj

# +-------------------------------------------------------------+
# | Logging                                                     |
# +-------------------------------------------------------------+

def log(*msg, tag="Utils"):
    """Prints to FreeCAD Console"""
    App.Console.PrintMessage("[{0}] {1}\n".format(tag, ' '.join((str(i) for i in msg))))

def log_err(*msg, tag="Utils"):
    """Prints to FreeCAD Console"""
    App.Console.PrintError("[{0}] {1}\n".format(tag, ' '.join((str(i) for i in msg))))

def def_log(tag):
    def fn(*msg):
        return log(*msg, tag=tag)
    return fn

def def_log_err(tag):
    def fn(*msg):
        return log_err(*msg, tag=tag)
    return fn

# +-------------------------------------------------------------+
# | Task Panel                                                  |
# +-------------------------------------------------------------+

def show_task_panel(widget):    
    from freecad.mnesarco.gui import Gui
    Gui.Control.closeDialog()
    execute_later(lambda: Gui.Control.showDialog(widget), 10)

def close_task_panel(do_after=None):
    from freecad.mnesarco.gui import Gui
    Gui.Control.closeDialog()
    if do_after:
        execute_later(do_after, 10)
