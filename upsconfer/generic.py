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
        """
        Returns the current SNMP client configuration:

        ```
        {
            'default': {
                'community': 'public',
                'access': 'none'
            },
            '1': {
                'ip': '10.8.7.6',
                'community': 'public',
                'access': 'ro',
            },
            '2': {
                'ip': '10.66.66.66',
                'community': 'secret1',
                'access': 'rw'
            },
        }
        ```

        * `default` key represents all other management stations.
        * `ip` is the address or subnet (if supported by device) of the SNMP client.
        * `access` is one of `none`, `ro` or `rw`.
        * `ip`, `community` and `access` keys are mandatory.

        :return: dict
        """
        raise NotImplementedError()

    def set_snmp_config(self, new_config):
        """
        Sets SNMP configuration from new_config dict.

        Optional keys that are not supported by this device type are silently ignored.

        :param new_config: configuration that will be applied to the device. Uses the same structure as returned by get_snmp_config().
        :return: bool
        """
        raise NotImplementedError()

    def get_trap_config(self):
        """
        Returns SNMP Trap configuration.

        ```
        {
            '1': {
                'ip': '10.6.8.7',
                'community': 'public',
                'version': 2,
                'severity': 'info',
                'type': 'rfc',
                'alias': 'nms.example.com'
            }
        }
        ```

        * `ip` and `community` are mandatory. Other keys are optional.
        * `version` determines the version of SNMP traps that will be sent out. Should be one of 1 or 2.
        * `severity` determines the level of traps that should be sent to this reciever. Should be one of: `none`, `info`, `warn`, `crit`.
        * `type` specifies the MIB from which the traps will be sent out. Valid values are `rfc` or `proprietary`.
        * `alias` is a user friendly display name for this trap reciever.

        :return: dict
        """
        raise NotImplementedError()

    def set_trap_config(self, new_config):
        """
        Sets SNMP trap configuration from new_config dict.

        Optional keys that are not supported by this device type are silently ignored.
        :param new_config: configuration that will be applied to the device. Uses the same structure as returned by get_trap_config().
        :return: bool
        """
        raise NotImplementedError()

    def get_serial(self):
        """
        :return: device serial number as a string
        """
        raise NotImplementedError()

    def get_info(self):
        """
        Returns a dict with device info.
        ```
        {
            'manufacturer': 'Socomec',
            'model': 'NETYS RT 1/1 UPS',
            'serial': '123456789',
            'firmware': '1.0',
            'agent_type': 'NetVision',
            'agent_firmware': '2.0h',
            'agent_serial': 'D1111',
            'mac_address': '00:11:22:33:44:55',
            'rating_va': '2200',
            'rating_w': '1900',
            'battery_capacity_ah': '7',
        }
        ```
        :return: dict
        """
        raise NotImplementedError()
