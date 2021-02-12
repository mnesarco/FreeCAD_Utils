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

from pathlib import Path


def resolve_path(file, reference_file):
    """Returns absolute path to `file`, using `reference_file` to resolve relative paths"""
    file_path = Path(file)
    if not file_path.is_absolute():
        file_path = Path(reference_file).parent.joinpath(file_path)
    return file_path


def make_path_relative(path, reference_path):
    return Path(path).relative_to(Path(reference_path).parent)
