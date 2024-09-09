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

from typing import Dict, List
from xml.sax.handler import ContentHandler
import xml.sax
import xml.parsers.expat
from itertools import chain

class Group:
    xml_id: str
    children: List['Group']
    ids: List[str]

    def __init__(self, xml_id: str) -> None:
        self.xml_id = xml_id
        self.children = []
        self.ids = []

    def get_ids(self) -> List[str]:
        ids = [*self.ids]
        for sub in self.children:
            ids += sub.get_ids()
        return ids

class ExactGroups(ContentHandler):
    groups: Dict[str, Group]

    def __init__(self):
        self.groups = dict()
        self.stack = [Group('***')]

    def startElement(self, name, attrs):
        if 'id' in attrs:
            xml_id = attrs['id']
            if not xml_id:
                return
            if name == 'g':
                g = Group(xml_id)
                self.stack[-1].children.append(g)
                self.stack.append(g)
                self.groups[xml_id] = g
            else:
                self.stack[-1].ids.append(xml_id)


    def endElement(self, name):
        if name == 'g' and len(self.stack) > 1:
            self.stack.pop()


def parse_svg_groups(file_name: str) -> Dict[str, List[str]]:
    """
    Parse the SVG file and extract a mapping of group and its children.

    :param str file_name: svg file path
    :return Dict[str, List[str]]: Map of group id to all children ids
    """
    parser = xml.sax.make_parser()
    handler = ExactGroups()
    parser.setContentHandler(handler)
    with open(file_name) as svg:
        parser.parse(svg)
    return handler.groups
