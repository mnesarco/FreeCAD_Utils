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

import ast, hashlib, json, re
from pathlib import Path
from freecad.mnesarco import App
from freecad.mnesarco.utils import strings
from freecad.mnesarco.utils import preferences
from freecad.mnesarco.remote import page
from freecad.mnesarco.resources import tr
from freecad.mnesarco.remote.exports import export_file, export_macro

class MacroWrapper:

    def __init__(self, path):
        code = ast.parse(path.read_bytes(), str(path), mode="exec")
        self.file = str(path)
        self.key = hashlib.sha256(str(path).encode()).hexdigest()
        self.name = path.stem
        
        defined_icon = None
        for node in code.body:
            if isinstance(node, ast.Assign):
                assign_name = node.targets[0].id
                if assign_name == '__Name__' and node.value.s:
                    self.name = node.value.s
                elif assign_name == '__Icon__' and node.value.s:
                    defined_icon = path.parent.joinpath(node.value.s)

        self.name = " ".join(strings.camel_terms(self.name))

        custom_icon = assigned_icons.get(path.stem, None)
        if custom_icon:
            self.icon = custom_icon
        elif defined_icon and defined_icon.exists():
            self.icon = defined_icon
        else:
            self.icon = path.parent.joinpath(path.stem + ".svg")
            if not self.icon.exists():
                self.icon = path.parent.joinpath(path.stem + ".png")
                if not self.icon.exists():
                    self.icon = None

        if self.icon:
            self.icon = str(self.icon)
        else:
            self.icon = get_next_icon(path.stem)

        self.icon = export_file(self.icon)
        export_macro(self)


class AllMacrosPage(page.Page):

    def title(self):
        return tr("All Macros")

    def sections(self):
        macros = get_all_macros()
        actions = [page.Action(m.name, m.icon, '/macro/{}'.format(m.key)) for m in macros]
        return [page.Section(tr("All"), actions)]


def get_all_macros():
    macros = []
    PATTERN = re.compile(r".*(\.FCMacro|.py)$", re.IGNORECASE)
    root = Path(App.getUserMacroDir(True))
    if not root.exists():
        root = Path(App.getUserMacroDir(False))
    for file in root.glob('*'):
        if PATTERN.match(file.name):
            try:
                macros.append(MacroWrapper(file))
            except (AttributeError, FileNotFoundError, SyntaxError):
                pass
    return macros



# -- Init generic icons
available_icons = preferences.get_mnesarco_pref('Remote', 'icons', 'macros', 'available')
if available_icons:
    available_icons = json.loads(available_icons)
else:
    available_icons = [i for i in range(1, 109)]

assigned_icons = preferences.get_mnesarco_pref('Remote', 'icons', 'macros', 'assigned')    
if assigned_icons:
    assigned_icons = json.loads(assigned_icons)
else:
    assigned_icons = {}

def get_next_icon(macro):
    global available_icons
    if len(available_icons) > 0:
        icon = "img/macro-icon-{}.svg".format(available_icons[0])
        available_icons = available_icons[1:]
        preferences.set_mnesarco_pref('Remote', 'icons', 'macros', 'available', json.dumps(available_icons))
        assigned_icons[macro] = icon
        preferences.set_mnesarco_pref('Remote', 'icons', 'macros', 'assigned', json.dumps(assigned_icons))
        return icon
    else:
        return 'img/macro.svg'


