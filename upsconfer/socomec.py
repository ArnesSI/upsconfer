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


import requests
import re
from hashlib import md5
import lxml.html
from upsconfer.exceptions import LoginFailure, SerialNotFound
from upsconfer.generic import UpsGeneric


class UpsSocomec(UpsGeneric):
    def login(self):
        login_page = requests.get('http://%s/' % self.host)
        m = re.search('NAME="Challenge" VALUE=\n"([^"]+)"', login_page.text, re.MULTILINE)
        if not m:
            raise LoginFailure()
        challenge = m.group(1)
        ch_str = '%s%s%s' % (self.user, self.password, challenge)
        response = md5(ch_str).hexdigest()
        data = {
            'Username': self.user,
            'Password': '',
            'Challenge': '',
            'Response': response
            }
        login_response = requests.post('http://%s/tgi/login.tgi' % self.host, data)
        if not login_response.ok:
            raise LoginFailure()
        self.cookies = login_response.cookies
        return True

    def get_snmp_config(self):
        response = requests.get('http://%s/net_snmpaccess1.htm' % self.host, cookies=self.cookies)
        response.raise_for_status()
        html = lxml.html.document_fromstring(response.text)
        xp_ip = '//input[@name="NM{nr}"]/@value'
        xp_community = '//input[@name="CO{nr}"]/@value'
        xp_access = '//select[@name="PE{nr}"]/option[@selected]/@value'
        norm_ip = lambda addr: '.'.join([str(int(o)) for o in addr.split('.')])
        config = {}
        config['1'] = {'ip': '0.0.0.0'}
        config['1']['community'] = html.xpath(xp_community.format(nr=1))[0]
        config['1']['access'] = html.xpath(xp_access.format(nr=1))[0]
        for i in range(2, 9):
            config[str(i)] = {'ip': norm_ip(html.xpath(xp_ip.format(nr=i))[0])}
            config[str(i)]['community'] = html.xpath(xp_community.format(nr=i))[0]
            config[str(i)]['access'] = html.xpath(xp_access.format(nr=i))[0]
        return config

    def set_snmp_config(self, new_config):
        config = self.get_snmp_config()
        config.update(new_config)
        data = {}
        data['CO1'] = config['1']['community']
        data['PE1'] = config['1']['access']
        for i in range(2, 9):
            data['NM%d' % i] = config[str(i)]['ip']
            data['CO%d' % i] = config[str(i)]['community']
            data['PE%d' % i] = config[str(i)]['access']
        response = requests.post('http://%s/tgi/net_snmpaccess1.tgi' % self.host,
            cookies=self.cookies,
            data=data)
        response.raise_for_status()
        return True

    '''
    NMS1:<ip>
    COM1:<community>
    PER1:<severity>[non|inf|war|sev]
    TTT1:<version>[0|1](SNMPv1|SNMPv2c)
    TYP1:<type>[v4|rfc](DV4|RFC1628)
    NMS2:0.0.0.0
    COM2:
    PER2:non
    TTT2:0
    TYP2:v4
    ...
    TYP8:v4
    '''
    def get_trap_config(self):
        response = requests.get('http://%s/net_snmptrap.htm' % self.host, cookies=self.cookies)
        response.raise_for_status()
        html = lxml.html.document_fromstring(response.text)
        xp_ip = '//input[@name="NMS{nr}"]/@value'
        xp_community = '//input[@name="COM{nr}"]/@value'
        xp_severity = '//select[@name="PER{nr}"]/option[@selected]/@value'
        xp_ver = '//select[@name="TTT{nr}"]/option[@selected]/@value'
        xp_type = '//select[@name="TYP{nr}"]/option[@selected]/@value'
        config = {}
        for i in range(1, 9):
            config[str(i)] = {'ip': html.xpath(xp_ip.format(nr=i))[0]}
            config[str(i)]['community'] = html.xpath(xp_community.format(nr=i))[0]
            config[str(i)]['severity'] = html.xpath(xp_severity.format(nr=i))[0]
            config[str(i)]['version'] = html.xpath(xp_ver.format(nr=i))[0]
            config[str(i)]['type'] = html.xpath(xp_type.format(nr=i))[0]
        return config

    def set_trap_config(self, new_config):
        config = self.get_snmp_config()
        config.update(new_config)
        data = {'Submit': 'Submit'}
        for i in range(1, 9):
            data['NMS%d' % i] = config[str(i)]['ip']
            data['COM%d' % i] = config[str(i)]['community']
            data['PER%d' % i] = config[str(i)]['severity']
            data['TTT%d' % i] = config[str(i)]['version']
            data['TYP%d' % i] = config[str(i)]['type']
        response = requests.post('http://%s/tgi/net_trapaccess.tgi' % self.host,
            cookies=self.cookies,
            data=data)
        response.raise_for_status()
        return True

    def get_serial(self):
        txt = self._get_info_text()
        m = re.search('Serial Number:</td>\n<td WIDTH="50%" CLASS="bold">([^<]+)', txt, re.MULTILINE)
        if not m:
            raise SerialNotFound()
        return m.group(1)

    def _get_info_text(self):
        response = requests.get('http://%s/info_ident.htm' % self.host, cookies=self.cookies)
        response.raise_for_status()
        return response.text
