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

VER_PATTERN = r'(?P<maj>\d+)\.(?P<min>\d+)\.(?P<rev>\d+)'

targets = [
    ('../../package.xml', re.compile(f'(<version>){VER_PATTERN}(</version>)')),
    ('../../manifest.ini', re.compile(f'(version=){VER_PATTERN}')),
    ('./__init__.py', re.compile(f'(__version__ = "){VER_PATTERN}(")')),
]

def repl(m: re.Match[str]) -> str:
    pre, maj, min, rev, *pos = m.groups()
    return f"{pre}{maj}.{min}.{int(rev)+1}{''.join(pos)}"

for f, pat in targets:
    with open(f, 'r') as fin:
        content = fin.read()
    with open(f, 'w') as fout:
        fout.write(pat.sub(repl, content))