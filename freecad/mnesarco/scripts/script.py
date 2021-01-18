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

import ast
from enum import Enum

from freecad.mnesarco import App
from freecad.mnesarco.utils.dialogs import error_dialog
from freecad.mnesarco.resources import Icons
from freecad.mnesarco.utils.extension import DocumentObject, DocumentObjectGui, Property, log, show_task_panel
from freecad.mnesarco.utils.editor import CodeEditorPanel
from freecad.mnesarco.resources import tr, get_template
from freecad.mnesarco.utils.files import resolve_path, make_path_relative


ModuleCache = dict()

class ParamMode(Enum):
    FUNCTION = 1
    VARIABLE = 2

class Param:

    __slots__ = ('name', 'doc', 'time', 'mode', 'section')

    def __init__(self, mode, name, doc = "", time = False, section = "Variables"):
        self.mode = mode
        self.name = name
        self.doc = doc
        self.time = time
        self.section = section

    def __call__(self, t):
        value = globals()[self.name]
        if callable(value):
            if (self.time):
                return value(t)
            else:
                return value()
        else:
            return value

    def set_property(self, obj, t, update = True):
        prop_type, value = get_property_info(self(t))
        if hasattr(obj, self.name) and update:
            obj.__setattr__(self.name, value)
        elif not hasattr(obj, self.name):
            obj.addProperty(prop_type, self.name, self.section, self.doc, 1 if self.mode == ParamMode.FUNCTION else 0)
            obj.__setattr__(self.name, value)

    def extract_to_global(self, obj):
        globals()[self.name] = getattr(obj, self.name, None)


class Script:

    __slots__ = ('functions', 'variables', 'code', 'symbols')

    def __init__(self, name, source):
        module = ast.parse(source, name, "exec")
        self.code = compile(module, name, "exec")
        functions = []
        variables = []
        symbols = []
        section = "Variables"
        for node in module.body:
            if isinstance(node, ast.FunctionDef):
                functions.append(Param(ParamMode.FUNCTION, node.name, 
                        doc=ast.get_docstring(node) or "", 
                        time=len(node.args.args) > 0 or node.args.vararg,
                        section=section
                    )
                )
                symbols.append(node.name)
            elif isinstance(node, ast.Assign):
                assign_name = node.targets[0].id
                if assign_name == 'SECTION':
                    section = node.value.s
                else:
                    variables.append(Param(ParamMode.VARIABLE, assign_name, 
                            doc="", 
                            time=False,
                            section=section
                        )
                    )
                    symbols.append(assign_name)
        self.functions = functions
        self.variables = variables
        self.symbols = symbols

    def exec(self):
        exec(self.code, globals())


def get_real_path(obj):    
    
    if obj.File:
        file_path = obj.File
    else:
        file_path = obj.Name + ".py"
        obj.File = file_path

    file_path = resolve_path(file_path, App.ActiveDocument.FileName)
    if not file_path.exists():
        try:
            file_path.write_text(get_template("scripts", "default_script.py.txt"))
        except BaseException:
            error_dialog(tr("Script file '{}' cannot be created").format(str(file_path)), raise_exception=True)

    return file_path


def load_script(file_path):
    try:
        return file_path.read_text()
    except BaseException:
        error_dialog(tr("Script file '{}' cannot be read").format(str(file_path)), raise_exception=True)
    

def get_property_info(value):
    if isinstance(value, (int, float)):
        prop_type = Property.Float
        value = float(value)
    elif isinstance(value, (list, tuple)) and all(isinstance(x, (float, int)) for x in value):
        prop_type = Property.FloatList
        value = [float(x) for x in value]
    elif isinstance(value, tuple) and all(isinstance(x, str) for x in value):
        prop_type = Property.Enumeration
    elif isinstance(value, list) and all(isinstance(x, str) for x in value):
        prop_type = Property.StringList        
    else:
        prop_type = Property.String
        value = str(value)
    return prop_type, value



class ScriptObjectGui(DocumentObjectGui):

    Icon = Icons.variables

    def __init__(self, vobj):
        super(ScriptObjectGui, self).__init__(vobj)

    def doubleClicked(self, vobj):
        show_task_panel(CodeEditorPanel(self.Object.Name, get_real_path(self.Object)))



class ScriptObject(DocumentObject):

    Persist = [('mtime', 0)]

    def __init__(self, obj):
        super(ScriptObject, self).__init__(obj)
        self.mtime = 0
        obj.addProperty(Property.Integer, 'Time', 'Base', tr('Current tick')).Time = 0
        obj.addProperty(Property.File, 'File', "Base", tr("Python script")).File = obj.Name + ".py"
        obj.addProperty(Property.String, 'RealName', "Base", tr("Real name usable in expressions"), 
            Property.Flag_ReadOnly).RealName = obj.Name
        obj.addProperty(Property.StringList, 'Symbols', "Base", "", Property.Flag_Hidden).Symbols = []


    @staticmethod
    def build_module(file_path, obj):
        script = load_script(file_path)
        try:
            module = Script(obj.Name, script)
            ModuleCache[obj] = module
        except BaseException as e:
            error_dialog(
                tr("Error parsing your script file: {0}: {1}. Check report window for details")
                .format(obj.Name, obj.File), 
                exception=e)
        else:
            try:
                module.exec()
                return module
            except BaseException as e:
                error_dialog(
                    tr("Error executing your script file: {0}: {1}. Check report window for details")
                    .format(obj.Name, obj.File), 
                    exception=e)

    @staticmethod
    def update_symbols(module, obj, time):
        # Initialize independent variables
        for var in module.variables:
            var.set_property(obj, time, update=False)

        # Put independent variables in scope (global)
        for var in module.variables:
            var.extract_to_global(obj)

        # Set dependent variables
        for func in module.functions:
            func.set_property(obj, time, update=True)

        # Clean removed variables
        if obj.Symbols:
            deleted = []
            for s in obj.Symbols:
                if s not in module.symbols:
                    deleted.append(s)
            for s in deleted:
                try:
                    obj.removeProperty(s)
                except BaseException:
                    pass
        obj.Symbols = module.symbols.copy()


    def execute(self, obj):

        # Fix label to avoid confusions
        obj.Label = obj.Name

        if not App.ActiveDocument.FileName:
            error_dialog(tr("You must save the current document before adding scripts"), raise_exception=True)

        if not obj.File:
            return

        # Make File Relative if possible
        try:
            obj.File = make_path_relative(obj.File, App.ActiveDocument.FileName)
        except ValueError:
            pass

        file_path = get_real_path(obj)

        # Manage cache
        if self.mtime < file_path.stat().st_mtime:
            self.mtime = file_path.stat().st_mtime
            ModuleCache[obj] = None

        # Big Bang
        time = obj.Time
        globals()['TIME'] = time

        # Execute
        module = ModuleCache.get(obj, None)
        if module:
            log(tr("Executing {} from cache").format(obj.Name))
        else:
            log(tr("Executing {} from {}").format(obj.Name, str(file_path)))
            module = ScriptObject.build_module(file_path, obj)

        ScriptObject.update_symbols(module, obj, time)

    @staticmethod
    def create_object(obj_name):
        if not App.ActiveDocument:
            App.newDocument()
        
        old = App.ActiveDocument.getObject(obj_name)
        if old:
            obj = old
        else:
            obj = DocumentObject.create(obj_name, ScriptObject, ScriptObjectGui)
        App.ActiveDocument.recompute()
        return obj

    @staticmethod
    def create():       
        from .dialogs import CreatePanel
        dialog = CreatePanel(ScriptObject.create_object)
        show_task_panel(dialog)
