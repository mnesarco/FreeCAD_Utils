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
# Mnesarco Utils is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Mnesarco Utils.  If not, see <http://www.gnu.org/licenses/>.
# 

import re
from freecad.mnesarco.resources import tr

INTEGER = re.compile(r'^-?\d+$')
FLOAT = re.compile(r'^-?\d+(\.\d+)$')

def push_message(messages, message):
    if messages is not None:
        messages.append(message)

def validate_num(value, converter, pattern, messages, min, max, name):
    if not pattern.match(value):
        push_message(messages, tr('Invalid {}').format(name))
        return False
    numval = converter(value)
    if min is not None and min > numval:
        push_message(messages, tr('Minimum allowed is {}').format(min))
        return False
    if max is not None and max < numval:
        push_message(messages, tr('Maximum allowed is {}').format(max))
        return False
    return True


def validate_int(value, min=None, max=None, messages=None):
    return validate_num(value, int, INTEGER, messages, min, max, 'Integer')

def validate_float(value, min=None, max=None, messages=None):
    return validate_num(value, float, FLOAT, messages, min, max, 'Number')

def validate_required(value, messages=None):
    if not value or not str(value).strip():
        push_message(messages, tr('Required'))
        return False
    return True