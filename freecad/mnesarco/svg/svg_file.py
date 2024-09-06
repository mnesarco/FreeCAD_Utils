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

from typing import List, Tuple, Iterable
import FreeCAD as App  # type: ignore
import FreeCADGui as Gui # type: ignore
import importSVG as svg  # type: ignore
import Part  # type: ignore
import re
from pathlib import Path
from itertools import count

import PySide.QtCore as QtCore # type: ignore
import PySide.QtGui as QtGui # type: ignore

from freecad.mnesarco.vendor.fpo import (
    proxy, 
    view_proxy, 
    PropertyFile, 
    PropertyFileIncluded, 
    PropertyStringList, 
    PropertyMode)

SELECTOR_PATTERN = re.compile(r'((?P<name>\w+)\s*:\s*)?\s*(?P<pat>.*)')
WORD_PATTERN = re.compile(r'\w+')


def select(pattern: str, doc: App.Document, shapes: bool = True) -> List[Part.Shape | App.DocumentObject]:
    """
    Extracts objects from the imported svg document using pattern to match ids.

    :param str pattern: regex to match svg node ids.
    :param App.Document doc: Source document.
    :param bool shapes: if true, the Shape is extracted, the DocumentObject otherwise.
    :return List[Part.Shape | App.DocumentObject]: all matching objects.
    """
    pat = re.compile(pattern)
    result = []
    for obj in doc.Objects:
        if pat.fullmatch(obj.Name) and hasattr(obj, 'Shape'):
            if shapes:
                result.append(obj.Shape.copy())
            else:
                result.append(obj)
    return result


def upsert(shape: Part.Shape, name: str, doc: App.Document) -> App.DocumentObject:
    """
    Insert or update Object's Shape.

    :param Part.Shape shape: The new Shape
    :param str name: Target object name
    :param App.Document doc: target document
    :return App.DocumentObject: updated or created object.
    """
    obj = doc.getObject(name)
    if not obj:
        obj = doc.addObject('Part::FeatureExt', name)
        obj.addExtension('Part::AttachExtensionPython')
    obj.Shape = shape
    return obj
    

def parse_selector(name: str|None, pattern: str|None, id_prefix: str, id_gen: count) -> Tuple[str, re.Pattern] | None:
    """
    Parse selectors into valid name, pattern objects

    :param str | None name: name
    :param str | None pattern: pattern
    :param str id_prefix: prefix for generated names
    :param count id_gen: sequence of generated ids
    :return Tuple[str, re.Pattern] | None: parsed pair
    """
    if not isinstance(name, str):
        name = ''
    if not isinstance(pattern, str):
        pattern = ''        
    
    name = name.strip()
    pattern = pattern.strip()

    # No pattern -> no match
    if not pattern:
        return None

    # in case of only a word, it is used as name and pattern
    # example> path1
    if not name and WORD_PATTERN.fullmatch(pattern):
        name = pattern
    
    # name MUST be a word or generated id
    if not WORD_PATTERN.fullmatch(name):
        name = f'{id_prefix}_{next(id_gen)}'

    # comma separated patterns are allowed for the same target
    # example> holes: h1, h2, h3
    if ',' in pattern:
        pattern = "|".join(f'({v.strip()})' for v in pattern.split(','))

    return name, re.compile(pattern)


def parse_selectors(select: List[str], id_prefix: str) -> Iterable[Tuple[str, re.Pattern]]:
    """
    Parse selectors into (name, pattern)

    :param List[str] select: selectors
    :return List[tuple[str, str]]: tuples of (name, regex)
    """
    matches = (SELECTOR_PATTERN.match(p) for p in select)
    parsed = (parse_selector(m.group('name'), m.group('pat'), id_prefix, count(1)) for m in matches)
    return (p for p in parsed if p)


@view_proxy(icon="self:../resources/icons/svg.svg")
class SvgFileView:

    def is_valid_file(self) -> bool:
        return self.Object.SourceFile and Path(self.Object.SourceFile).exists()

    def on_context_menu(self, vp, menu):
        if self.is_valid_file():
            action_sync = QtGui.QAction('Sync svg file', menu)
            QtCore.QObject.connect(action_sync,
                                QtCore.SIGNAL("triggered()"),
                                self.sync_svg)
            menu.addAction(action_sync)

    def sync_svg(self):
        if self.is_valid_file():
            self.Object.File = self.Object.SourceFile
            self.Object.recompute()
            self.Object.Document.recompute()


@proxy(object_type='App::DocumentObjectGroupPython', view_proxy=SvgFileView)
class SvgFile:
    source_file = PropertyFile(description = 'Path to the external svg file')
    file = PropertyFileIncluded(description = 'Path to the internal svg file', mode=PropertyMode.Hidden)
    select = PropertyStringList(description="Id Patterns", default=['all:.*'])

    @source_file.observer
    def on_source_change(self, obj, path):
        self.file = path

    def on_change(self, obj, prop_name, value, old):
        if prop_name != 'SourceFile':
            self.on_execute(obj)

    def on_execute(self, obj):
        if self.file and Path(self.file).exists() and self.select:
            doc_name = App.ActiveDocument.Name
            svg_doc: App.Document = App.newDocument('_svg_import_', hidden=True, temp=True)
            svg.insert(self.file, svg_doc.Name)
            App.setActiveDocument(doc_name)

            old_children = dict()
            if obj.Group:
                old_children = {c.Name: True for c in obj.Group}

            for name, pattern in parse_selectors(self.select, obj.Name):
                shapes = select(pattern, svg_doc, True)
                if shapes:
                    child = upsert(Part.makeCompound(shapes), name, App.ActiveDocument)
                    if child.Name not in old_children:
                        obj.addObject(child)
                    old_children[child.Name] = False

            App.closeDocument(svg_doc.Name)
            
            for name, remove in old_children.items():
                if remove:
                    App.ActiveDocument.removeObject(name)

            Gui.Selection.clearSelection()
            Gui.Selection.addSelection(doc_name, obj.Name)

            
