# Copyright (C) 2021 Frank David Martinez M. <https://github.com/mnesarco/>
#
# This file is part of Mnesarco Utils.
#
# Mnesarco Utils is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mnesarco Utils is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mnesarco Utils.  If not, see <http://www.gnu.org/licenses/>.
#

from freecad.mnesarco.utils.toolbars import add_global_action
from freecad.mnesarco.resources import Icons, tr
from freecad.mnesarco.utils.extension import App, def_log

log_err = def_log('Files')

def init_files():
    add_global_action(
        name="SaveAsNextFile",
        icon=Icons.save_next,
        action=cmd_save_as_next_file,
        menu=tr("Save current document and open as next file"),
        activation=lambda: App.Gui.activeDocument()
    )

def cmd_save_as_next_file():
    import re
    from pathlib import Path
    doc = App.ActiveDocument
    try:
        doc.save()
    except Exception:
        App.Gui.SendMsgToActiveView("SaveAs")
        return

    name = doc.FileName
    sep = r'_next'
    pat = re.compile(rf'(.*?)({sep}(\d+))?\.FCStd')
    m = pat.fullmatch(name)
    if m:
        prefix, _, num = m.groups()
        num = int(num) + 1 if num is not None else 1
        next_name = Path(f"{prefix}{sep}{num:03d}.FCStd")
        while next_name.exists():
            num += 1
            next_name = Path(f"{prefix}{sep}{num:03d}.FCStd")
        doc.saveAs(str(next_name))
    else:
        log_err("Only .FCStd files are supported")