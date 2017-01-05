# -*- coding: utf-8 -*-
########################################################################
#
# (C) 2017, Matej Vadnjal, Arnes <matej@arnes.si> <matej@vadnjal.net>
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

"""
Generic class that vendor specific classes should inherit from.
"""


class UpsGeneric(object):
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password
        self.cookies = None

    def login(self):
        raise NotImplementedError()

    def get_snmp_config(self):
        raise NotImplementedError()

    def set_snmp_config(self, new_config):
        raise NotImplementedError()

    def get_trap_config(self):
        raise NotImplementedError()

    def set_trap_config(self, new_config):
        raise NotImplementedError()

    def get_serial(self):
        raise NotImplementedError()
