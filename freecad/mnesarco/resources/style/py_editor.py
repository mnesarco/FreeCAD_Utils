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

from . import merge

base_background = "#eeeeee"

styles = dict(
    background = base_background,
    text = "#222222",
    font_size = 12,
    scrollbar_background = "transparent",
    scrollbar_width = 15,
    scrollbar_handle_min_size = 20,
    scrollbar_handle_color = "#222222",
    scrollbar_border = "0px solid transparent",
)

template = """
QWidget {
     background: {{background}}; 
     color: {{text}}; 
     font-size: {{font_size}}pt;
     font-family: Courier
}

QScrollBar:horizontal {
    border: {{scrollbar_border}};
    background: {{scrollbar_background}};
    height: {{scrollbar_width}}px;
    margin: 0 {{scrollbar_width}}px 0 0;
}

QScrollBar:vertical {
    border: {{scrollbar_border}};
    background: {{scrollbar_background}};
    width: {{scrollbar_width}}px;
    margin: 0 0 {{scrollbar_width}}px 0;
}

QScrollBar::handle:horizontal {
    background: {{scrollbar_handle_color}};
    min-width: {{scrollbar_handle_min_size}}px;
}

QScrollBar::handle:vertical {
    background: {{scrollbar_handle_color}};
    min-height: {{scrollbar_handle_min_size}}px;
}

"""

stylesheet = merge(template, styles)

