# -*- coding: utf-8 -*-
########################################################################
#
# (C) 2017, Matej Vadnjal, Arnes <matej> <matej@vadnjal.net>
#
# This file is part of upsconfer
#
# upsconfer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# upsconfer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with upsconfer.  If not, see <http://www.gnu.org/licenses/>.
#
########################################################################


def char_range(c1, c2):
    """Generates the characters from `c1` to `c2`, inclusive.
       http://stackoverflow.com/a/7001371
    """
    for c in xrange(ord(c1), ord(c2)+1):
        yield chr(c)


def get_list_item(l, idx=0, default=None):
    if not l or idx >= len(l):
        return default
    return l[idx]


def get_dict_key(d, value, default=None):
    if value not in d.values():
        return default
    return d.keys()[d.values().index(value)]
