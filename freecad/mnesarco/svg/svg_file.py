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

import re
from contextlib import suppress
from itertools import count
from pathlib import Path
from typing import Iterable, List, Tuple

import FreeCAD as App  # type: ignore
import FreeCADGui as Gui  # type: ignore
import importSVG as svg  # type: ignore
import Part  # type: ignore
import PySide.QtCore as QtCore  # type: ignore
import PySide.QtGui as QtGui  # type: ignore

from freecad.mnesarco.utils.extension import def_log
from freecad.mnesarco.vendor.fpo import (
    PropertyBool,
    PropertyFile,
    PropertyFileIncluded,
    PropertyMode,
    PropertyStringList,
    proxy,
    view_proxy,
    Preference
)

log_err = def_log('SvgFile')

# Preferences
default_import_as_sketch = Preference(group="MnesarcoUtils/Svg", name="Import as Sketch", default=False)

SELECTOR_PATTERN = re.compile(r'((?P<name>\w+)\s*:\s*)?\s*(?P<pat>.*)')
WORD_PATTERN = re.compile(r'\w+')

def select(pattern: re.Pattern, doc: App.Document) -> List[Part.Shape]:
    """
    Extracts objects from the imported svg document using pattern to match ids.

    :param str pattern: regex to match svg node ids.
    :param App.Document doc: Source document.
    :return List[Part.Shape | App.DocumentObject]: all matching objects.
    """
    result = []
    for obj in doc.Objects:
        if pattern.fullmatch(obj.Name) and hasattr(obj, 'Shape') and obj.Shape:
            result.append(obj.Shape.copy())
    return result


def upsert(shape: Part.Shape, name: str, doc: App.Document, parent: App.DocumentObject, as_sketch: bool) -> App.DocumentObject:
    """
    Insert or update Object's Shape.

    :param Part.Shape shape: The new Shape
    :param str name: Target object name
    :param App.Document doc: target document
    :return App.DocumentObject: updated or created object.
    """
    obj = doc.getObject(name)
    if as_sketch:
        import Draft  # type: ignore
        if obj:
            if hasattr(obj, 'delGeometries'):
                obj.delGeometries([i for i in range(obj.GeometryCount)])
                Draft.make_sketch(shape, autoconstraints=True, addTo=obj)
            else:
                doc.removeObject(name)
                obj = Draft.make_sketch(shape, autoconstraints=True, name=name)
        else:
            obj = Draft.make_sketch(shape, autoconstraints=True, name=name)
        parent.addObject(obj)
    else:
        if obj and hasattr(obj, 'delGeometries'):
            doc.removeObject(name)
            obj = None
        if not obj:
            obj = doc.addObject('Part::FeatureExt', name)
            obj.Label = name
            obj.addExtension('Part::AttachExtensionPython')
        obj.Shape = shape
        if not obj.getParent():
            parent.addObject(obj)
    return obj


def parse_selector(name: str|None, pattern: str|None, id_prefix: str, id_gen: count) -> Tuple[str, re.Pattern, str] | None:
    """
    Parse selectors into valid name, pattern objects

    :param str | None name: name
    :param str | None pattern: pattern
    :param str id_prefix: prefix for generated names
    :param count id_gen: sequence of generated ids
    :return Tuple[str, re.Pattern, str] | None: (name, parsed pattern, raw pattern)
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

    src_pattern = pattern

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

    return name, re.compile(pattern), src_pattern


def parse_selectors(select: List[str], id_prefix: str) -> Iterable[Tuple[str, re.Pattern]]:
    """
    Parse selectors into (name, pattern)

    :param List[str] select: selectors
    :return List[tuple[str, str]]: tuples of (name, regex)
    """
    matches = (SELECTOR_PATTERN.match(p) for p in select)
    parsed = (parse_selector(m.group('name'), m.group('pat'), id_prefix, count(1)) for m in matches if m)
    return (p for p in parsed if p)


@view_proxy(icon="self:../resources/icons/svg.svg")
class SvgFileView:

    def is_valid_file(self) -> bool:
        return self.Object.SourceFile and Path(self.Object.SourceFile).exists()

    def on_context_menu(self, vp, menu):
        if self.is_valid_file():
            action_sync = QtGui.QAction('Sync svg file', menu)
            QtCore.QObject.connect(action_sync, QtCore.SIGNAL("triggered()"), self.sync_svg)
            menu.addAction(action_sync)

        action_recompute = QtGui.QAction('Deep recompute (Slow)', menu)
        QtCore.QObject.connect(action_recompute, QtCore.SIGNAL("triggered()"), self.deep_recompute)
        menu.addAction(action_recompute)

    def deep_recompute(self):
        children = self.Object.Group
        if children:
            for child in children:
                child.touch()
            self.Object.Document.recompute(None, True, True)

    def sync_svg(self):
        if self.is_valid_file():
            self.Object.File = self.Object.SourceFile
            self.Object.recompute()
            self.Object.Document.recompute(None, True, True)


@proxy(object_type='App::DocumentObjectGroupPython', view_proxy=SvgFileView)
class SvgFile:
    source_file = PropertyFile(description='Path to the external svg file')
    file = PropertyFileIncluded(description='Path to the internal svg file', mode=PropertyMode.Hidden)
    select = PropertyStringList(description="Id Patterns", default=['all:.*'])
    as_sketches = PropertyBool(description="Import geometry as sketches", default=False)

    def on_create(self, obj):
        self.as_sketches = default_import_as_sketch()

    @source_file.observer
    def on_source_change(self, obj, path):
        self.file = path


    def on_change(self, obj, prop_name, value, old):
        if prop_name != 'SourceFile' and prop_name != 'Shape':
            self.on_execute(obj)


    def get_selection(self, obj: App.DocumentObject) -> Tuple[List[Tuple[str, re.Pattern, str]], bool]:
        """
        Parse and rename selections if necessary
        """
        result = []
        changed = False
        doc = obj.Document
        for name, pattern, src_pattern in parse_selectors(self.select, obj.Name):
            child = doc.getObject(name)
            if not child or child.getParent() is obj:
                result.append((name, pattern, src_pattern))
            else:
                result.append((f"{obj.Name}_{name}", pattern, src_pattern))
                changed = True
        return result, changed


    def extract_by_pattern(self, selection, not_found, new_children, svg_doc):
        for name, pattern, raw_pattern in selection:
            shapes = select(pattern, svg_doc)
            if shapes:
                new_children.append((Part.makeCompound(shapes), name))
            else:
                not_found.append((name, raw_pattern))


    def extract_by_group(self, not_found, new_children, svg_doc):
        from .parser import parse_svg_groups
        groups = parse_svg_groups(self.file)
        if groups:
            for name, xml_id in not_found:
                group = groups.get(xml_id, None)
                if group:
                    shapes = []
                    for obj_id in group.get_ids():
                        child = svg_doc.getObject(obj_id)
                        if child and hasattr(child, 'Shape') and child.Shape:
                            shapes.append(child.Shape.copy())
                    if shapes:
                        new_children.append((Part.makeCompound(shapes), name))
                    else:
                        log_err(f"Empty group: {name}: {xml_id}")
                else:
                    log_err(f"Group not found: {name}: {xml_id}")


    def on_execute(self, obj):
        selection, selection_changed = self.get_selection(obj)
        if selection_changed:
            self.select = [f"{n}:{p}" for n,pp,p in selection]
            return

        if self.file and Path(self.file).exists() and self.select:
            doc_name = App.ActiveDocument.Name

            # save objects names for removal
            pending_for_remove = dict()
            if obj.Group:
                pending_for_remove = {c.Name: True for c in obj.Group}

            # Load svg file into a temporal document
            svg_doc: App.Document = App.newDocument('_svg_import_', hidden=True, temp=True)
            svg_doc_name = svg_doc.Name
            svg.insert(self.file, svg_doc.Name)

            # Extract objects by id pattern
            new_children = []
            not_found = []
            self.extract_by_pattern(selection, not_found, new_children, svg_doc)

            # Extract object not_found, looking for groups
            if not_found:
                self.extract_by_group(not_found, new_children, svg_doc)

            # Clean hidden import file
            with suppress(Exception):
                App.closeDocument(svg_doc_name)

            # Insert targets into current doc
            App.setActiveDocument(doc_name)
            updated_objects = []
            for shape, name in new_children:
                child = upsert(shape, name, App.ActiveDocument, obj, self.as_sketches)
                pending_for_remove[child.Name] = False
                updated_objects.append(child)

            # Clean orphan objects
            for name, remove in pending_for_remove.items():
                if remove and App.ActiveDocument.getObject(name):
                    App.ActiveDocument.removeObject(name)

            # Clear recompute
            for child in updated_objects:
                child.recompute()
                child.purgeTouched()

            # Restore selection
            Gui.Selection.clearSelection()
            Gui.Selection.addSelection(App.ActiveDocument.Name, obj.Name)
