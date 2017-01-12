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
import lxml.html
from upsconfer.exceptions import LoginFailure
from upsconfer.generic import UpsGeneric
from upsconfer.util import get_list_item
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# silence InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class UpsRielloSentinel(UpsGeneric):
    def login(self):
        data = {
            'username': self.user,
            'password': self.password,
            }
        response = requests.post('https://%s/cgi-bin/login.cgi' % self.host, data=data, verify=False)
        if not response.ok or not len(response.cookies):
            raise LoginFailure()
        self.cookies = response.cookies
        return True

    def get_snmp_config(self):
        """
        forms/riello/sentinel/snmp_config.html
        """
        response = requests.get('https://%s/cgi-bin/snmp_config.cgi' % self.host, cookies=self.cookies, verify=False)
        response.raise_for_status()
        html = lxml.html.document_fromstring(response.text)
        config = {}
        config['default'] = {}
        config['default']['community'] = get_list_item(html.xpath('//input[@id="snmp_cconfig0"]/@value'), 0, '').strip()
        config['default']['access'] = 'ro'
        return config

    def set_snmp_config(self, new_config):
        data = self._get_snmp_form()
        if new_config['default']['access'] == 'ro':
            data['snmp_cconfig0'] = new_config['default']['community']
        elif new_config['default']['access'] == 'rw':
            data['snmp_cconfig1'] = new_config['default']['community']
        response = requests.post('https://%s/cgi-bin/snmp_config_w.cgi' % self.host,
                                 cookies=self.cookies,
                                 data=data,
                                 verify=False)
        response.raise_for_status()
        return True

    def get_trap_config(self):
        """
        forms/riello/sentinel/snmp_config.html
        """
        response = requests.get('https://%s/cgi-bin/snmp_config.cgi' % self.host, cookies=self.cookies, verify=False)
        response.raise_for_status()
        html = lxml.html.document_fromstring(response.text)
        config = {}
        for i in range(0, 7):
            entry = {}
            entry['ip'] = get_list_item(html.xpath('//input[@id="snmp_config%d"]/@value' % i), 0, '').strip()
            entry['community'] = get_list_item(html.xpath('//input[@id="snmp_cconfig2"]/@value'), 0, '').strip()
            config[str(i+1)] = entry
        return config

    def set_trap_config(self, new_config):
        data = self._get_snmp_form()
        data['snmp_cconfig2'] = new_config['1']['community']
        for i in range(0, 7):
            if str(i+1) not in new_config:
                continue
            data['snmp_config%d' % i] = new_config[str(i+1)]['ip']
        response = requests.post('https://%s/cgi-bin/snmp_config_w.cgi' % self.host,
                                 cookies=self.cookies,
                                 data=data,
                                 verify=False)
        response.raise_for_status()
        return True

    def get_info(self):
        """
        forms/riello/sentinel/view_about.html
        """
        response = requests.get('https://%s/cgi-bin/view_about.cgi' % self.host, cookies=self.cookies, verify=False)
        response.raise_for_status()
        html = lxml.html.document_fromstring(response.text)
        xpaths = {
            'model': '//td[node()="Model"]/following-sibling::td/text()',
            'serial': '//td[node()="Identification number"]/following-sibling::td/text()',
            'firmware': '//td[node()="Firmware version"]/following-sibling::td/text()',
            'agent_firmware': '//td[node()="Application version"]/following-sibling::td/text()',
            'agent_serial': '//td[node()="Serial Number"]/following-sibling::td/text()',
            'mac_address': '//td[node()="MAC Address"]/following-sibling::td/text()',
            'rating_va': '//td[node()="Power [kVA]"]/following-sibling::td/text()',
            'rating_w': '//td[node()="Power [kW]"]/following-sibling::td/text()',
            'battery_capacity_ah': '//td[node()="Battery capacity [Ah]"]/following-sibling::td/text()',
        }
        info = {}
        info['manufacturer'] = 'Riello'
        info['agent_type'] = 'Netman 204'
        for k, xpath in xpaths.items():
            info[k] = get_list_item(html.xpath(xpath), 0, '').strip()
        if info.get('rating_va'):
            info['rating_va'] = str(int(float(info['rating_va']) * 1000))
        if info.get('rating_w'):
            info['rating_w'] = str(int(float(info['rating_w']) * 1000))
        return info

    def _get_snmp_form(self):
        # get current values from form
        response = requests.get('https://%s/cgi-bin/snmp_config.cgi' % self.host, cookies=self.cookies, verify=False)
        response.raise_for_status()
        html = lxml.html.document_fromstring(response.text)
        data = {}
        data['enable_snmp'] = 'on'
        for k in ['snmp_cconfig0', 'snmp_cconfig1', 'snmp_cconfig2', 'snmp_sysC', 'snmp_sysN', 'snmp_sysL', 'session']:
            data[k] = get_list_item(html.xpath('//input[@name="%s"]/@value' % k), 0, '').strip()
        for i in range(0, 7):
            data['snmp_config%d' % i] = get_list_item(html.xpath('//input[@name="snmp_config%d"]/@value' % i), 0, '').strip()
        return data

    def _logout(self):
        requests.get('https://%s/cgi-bin/logout.cgi' % self.host, cookies=self.cookies, verify=False)
        self.cookies = None
        return True

    def _reboot(self):
        requests.get('https://%s/cgi-bin/reboot_2.cgi' % self.host, cookies=self.cookies, verify=False)
        self.cookies = None
        return True
