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


import re
import requests
from hashlib import md5
import lxml.html
from upsconfer.exceptions import LoginFailure
from upsconfer.generic import UpsGeneric
from upsconfer.util import char_range, get_list_item, get_dict_key


class UpsSocomecNetys(UpsGeneric):
    MAP_SEV_PER = {
        'none': 'non',
        'info': 'inf',
        'warn': 'war',
        'crit': 'sec'
    }
    MAP_VER_TTT = {
        '1': '0',
        '2': '1'
    }
    MAP_TYPE_TYP = {
        'proprietary': 'v4',
        'rfc': 'rfc'
    }

    def login(self):
        """
        forms/socomec/netys/login.htm
        """
        response = requests.get('http://%s/' % self.host)
        response.raise_for_status()
        html = lxml.html.document_fromstring(response.text)
        xp_challenge = '//input[@name="Challenge"]/@value'
        challenge = html.xpath(xp_challenge)[0]
        if not challenge:
            LoginFailure('Could not find challenge.')
        ch_str = '%s%s%s' % (self.user, self.password, challenge)
        response = md5(ch_str).hexdigest()
        data = {
            'Username': self.user,
            'Password': '',
            'Challenge': '',
            'Response': response
            }
        response = requests.post('http://%s/tgi/login.tgi' % self.host, data)
        if not response.ok:
            raise LoginFailure()
        self.cookies = response.cookies
        return True

    def get_snmp_config(self):
        """
        forms/socomec/netys/net_snmpaccess1.htm
        """
        response = requests.get('http://%s/net_snmpaccess1.htm' % self.host, cookies=self.cookies)
        response.raise_for_status()
        html = lxml.html.document_fromstring(response.text)
        xp_ip = '//input[@name="NM{nr}"]/@value'
        xp_community = '//input[@name="CO{nr}"]/@value'
        xp_access = '//select[@name="PE{nr}"]/option[@selected]/@value'
        norm_ip = lambda addr: '.'.join([str(int(o)) for o in addr.split('.')])
        config = {}
        config['default'] = {'ip': '0.0.0.0'}
        config['default']['community'] = html.xpath(xp_community.format(nr=1))[0]
        config['default']['access'] = html.xpath(xp_access.format(nr=1))[0]
        for i in range(2, 9):
            config[str(i-1)] = {'ip': norm_ip(html.xpath(xp_ip.format(nr=i))[0])}
            config[str(i-1)]['community'] = html.xpath(xp_community.format(nr=i))[0]
            config[str(i-1)]['access'] = html.xpath(xp_access.format(nr=i))[0]
        return config

    def set_snmp_config(self, new_config):
        """
        Form structure:
        CO1: <default->community>
        PE1: <default->access>[valid values: none|ro|rw]
        NM2: <1->ip>
        CO2: <1->community>
        PE2: <1->access>
        ...
        PE8: <7->access>
        """
        config = self.get_snmp_config()
        config.update(new_config)
        data = {}
        data['CO1'] = config['default']['community']
        data['PE1'] = config['default']['access']
        for i in range(2, 9):
            data['NM%d' % i] = config[str(i-1)]['ip']
            data['CO%d' % i] = config[str(i-1)]['community']
            data['PE%d' % i] = config[str(i-1)]['access']
        response = requests.post('http://%s/tgi/net_snmpaccess1.tgi' % self.host,
                                 cookies=self.cookies,
                                 data=data)
        response.raise_for_status()
        return True

    def get_trap_config(self):
        """
        forms/socomec/netys/net_snmptrap.htm
        """
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
            config[str(i)]['severity'] = get_dict_key(self.MAP_SEV_PER, html.xpath(xp_severity.format(nr=i))[0])
            config[str(i)]['version'] = get_dict_key(self.MAP_VER_TTT, html.xpath(xp_ver.format(nr=i))[0])
            config[str(i)]['type'] = get_dict_key(self.MAP_TYPE_TYP, html.xpath(xp_type.format(nr=i))[0])
        return config

    def set_trap_config(self, new_config):
        """
        Form structure:
        NMS1:<1->ip>
        COM1:<1->community>
        PER1:<1->severity>[valid values: non|inf|war|sev (none|info|warn|crit)]
        TTT1:<1->version>[valid values: 0|1 (1|2)]
        TYP1:<1->type>[valid values: v4|rfc (proprietary|rfc)]
        NMS2:<2->ip>
        ...
        TYP8:<8->type>
        Submit: Submit
        """
        config = self.get_snmp_config()
        config.update(new_config)
        data = {'Submit': 'Submit'}
        for i in range(1, 9):
            data['NMS%d' % i] = config[str(i)]['ip']
            data['COM%d' % i] = config[str(i)]['community']
            data['PER%d' % i] = self.MAP_SEV_PER.get((config[str(i)]['severity']), 'non')
            data['TTT%d' % i] = self.MAP_VER_TTT.get(config[str(i)]['version'], '1')
            data['TYP%d' % i] = self.MAP_TYPE_TYP.get(config[str(i)]['type'], 'rfc')
        response = requests.post('http://%s/tgi/net_trapaccess.tgi' % self.host,
                                 cookies=self.cookies,
                                 data=data)
        response.raise_for_status()
        return True

    def get_info(self):
        """
        forms/socomec/netys/info_ident.htm
        """
        html = self._get_info_html()
        xpaths = {
            'model': '//td[text()="Model:"]/following-sibling::td/text()',
            'serial':'//td[text()="Serial Number:"]/following-sibling::td/text()',
            'firmware': '//td[text()="UPS Firmware:"]/following-sibling::td/text()',
            'agent_firmware': '//td[text()="Web Firmware:"]/following-sibling::td/text()',
            'rating_va': '//td[text()="Rating VA:"]/following-sibling::td/text()',
        }
        info = {}
        info['manufacturer'] = 'Socomec'
        info['agent_type'] = 'NetVision'
        for k, xpath in xpaths.items():
            info[k] = html.xpath(xpath)[0]
        info['rating_va'] = info['rating_va'].split(' ')[0]
        return info

    def _get_info_html(self):
        response = requests.get('http://%s/info_ident.htm' % self.host, cookies=self.cookies)
        response.raise_for_status()
        html = lxml.html.document_fromstring(response.text)
        return html


class UpsSocomecMasterys(UpsGeneric):
    MAP_ACCESS = {
        'ro': '1',
        'rw': '2',
        'none': '3'
    }

    def __init__(self, *args, **kwargs):
        self.auth = None
        super(UpsSocomecMasterys, self).__init__(*args, **kwargs)

    def login(self):
        # not an actual login, use http basic auth on every request
        self.auth = (self.user, self.password)
        response = requests.get('http://%s/PageMonComprehensive.html' % self.host, auth=self.auth)
        if not response.ok:
            raise LoginFailure()
        return True

    def get_snmp_config(self):
        """
        forms/socomec/masterys/PageAdmAgentAccess.html
        """
        response = requests.get('http://%s/PageAdmAgentAccess.html' % self.host, auth=self.auth)
        response.raise_for_status()
        html = lxml.html.document_fromstring(response.text)
        xp_ip = '//input[@name="XAAAAAAA{nr}AADE"]/@value'
        xp_community = '//input[@name="XAAAAAAA{nr}AADF"]/@value'
        xp_access = '//select[@name="XAAAAAAA{nr}AADG"]/option[@selected]/@value'
        config = {}
        idx = 1
        for i in char_range('B', 'I'):
            config[str(idx)] = {'ip': get_list_item(html.xpath(xp_ip.format(nr=i)), 0, '')}
            config[str(idx)]['community'] = html.xpath(xp_community.format(nr=i))[0]
            config[str(idx)]['access'] = get_dict_key(self.MAP_ACCESS, str(html.xpath(xp_access.format(nr=i))[0]), 'none')
            idx += 1
        # change the last entry into a default
        last_idx = str(idx-1)
        last_entry = config[last_idx]
        del(last_entry['ip'])
        config['default'] = last_entry
        del(config[last_idx])
        return config

    def set_snmp_config(self, new_config):
        """
        Form structure:
        XAAAAAAABAADE: <1->ip>
        XAAAAAAABAADF: <1->community>
        XAAAAAAABAADG: <1->access>[valid values: 1|2|3 (ro|rw|none)]
        XAAAAAAACAADE: <2->ip>
        XAAAAAAACAADF: <2->community>
        XAAAAAAACAADG: <2->access>[valid values: 1|2|3 (ro|rw|none)]
        ...
        XAAAAAAAIAADE: ''
        XAAAAAAAIAADF: <default->community>
        XAAAAAAAIAADG: <default->access>[valid values: 1|2|3 (ro|rw|none)]
        """
        config = self.get_snmp_config()
        config.update(new_config)
        data = {}
        idx = 1
        for i in char_range('B', 'H'):
            entry = config[str(idx)]
            data['XAAAAAAA%sAADE' % i] = entry['ip']
            data['XAAAAAAA%sAADF' % i] = entry['community']
            data['XAAAAAAA%sAADG' % i] = self.MAP_ACCESS.get(entry['access'], 'none')
            idx += 1
        data['XAAAAAAAIAADE'] = ''
        data['XAAAAAAAIAADF'] = config['default']['community']
        data['XAAAAAAAIAADG'] = self.MAP_ACCESS.get(config['default']['access'], 'none')
        response = requests.post('http://%s/PageAdmAgentAccess.html' % self.host,
                                 auth=self.auth,
                                 data=data)
        response.raise_for_status()
        return True

    def get_trap_config(self):
        """
        forms/socomec/masterys/PageAdmAgentTrap.html
        """
        response = requests.get('http://%s/PageAdmAgentTrap.html' % self.host, auth=self.auth)
        response.raise_for_status()
        html = lxml.html.document_fromstring(response.text)
        xp_ip = '//input[@name="XAAAAAAA{nr}AAFE"]/@value'
        xp_community = '//input[@name="XAAAAAAA{nr}AAFF"]/@value'
        xp_type = '//select[@name="XAAAAAAA{nr}AAFJ"]/option[@selected]/@value'
        xp_alias = '//input[@name="XAAAAAAA{nr}AAFG"]/@value'
        config = {}
        idx = 1
        for i in char_range('B', 'I'):
            entry = {'ip': get_list_item(html.xpath(xp_ip.format(nr=i)), 0, '')}
            entry['community'] = html.xpath(xp_community.format(nr=i))[0]
            type_device = get_list_item(html.xpath(xp_type.format(nr=i)), 0, '2')
            if type_device == '3':
                entry['severity'] = 'info'
                entry['type'] = 'rfc'
            elif type_device == '2':
                entry['severity'] = 'info'
                entry['type'] = 'proprietary'
            else:
                entry['severity'] = 'none'
                entry['type'] = 'rfc'
            entry['alias'] = get_list_item(html.xpath(xp_alias.format(nr=i)), 0, '')
            config[str(idx)] = entry
            idx += 1
        return config

    def set_trap_config(self, new_config):
        """
        Form structure:
        XAAAAAAABAAFE: <1->ip>
        XAAAAAAABAAFF: <1->community>
        XAAAAAAABAAFJ: <1->type|severity>[valid values: 1|2|3 (severity.none|type.proprietary|type.rfc)
        XAAAAAAABAAFG: <1->alias>
        XAAAAAAACAAFE: <2->ip>
        XAAAAAAACAAFF: <2->community>
        XAAAAAAACAAFJ: <2->type|severity>[valid values: 1|2|3 (severity.none|type.proprietary|type.rfc)
        XAAAAAAACAAFG: <2->alias>
        ...
        XAAAAAAAIAAFG: <8->alias>
        """
        config = self.get_trap_config()
        config.update(new_config)
        data = {}
        idx = 1
        for i in char_range('B', 'I'):
            entry = config[str(idx)]
            data['XAAAAAAA%sAAFE' % i] = entry['ip']
            data['XAAAAAAA%sAAFF' % i] = entry['community']
            if entry.get('severity', '') == 'none':
                typ = '1'
            elif entry.get('type', 'rfc') == 'proprietary':
                typ = '2'
            else:
                typ = '3'
            data['XAAAAAAA%sAAFJ' % i] = typ
            data['XAAAAAAA%sAAFG' % i] = entry.get('alias', '')
            idx += 1
        response = requests.post('http://%s/PageAdmAgentTrap.html' % self.host,
                                 auth=self.auth,
                                 data=data)
        response.raise_for_status()
        return True

    def get_info(self):
        """
        forms/socomec/modulys/PageMonIdentification.html
        """
        response = requests.get('http://%s/PageMonIdentification.html' % self.host, auth=self.auth)
        response.raise_for_status()
        html = lxml.html.document_fromstring(response.text)
        xpaths = {
            'model': '//td/*[text()="UPS Model"]/../following-sibling::td//td/*/text()',
            'serial': '//td/*[text()="UPS Serial Number"]/../following-sibling::td//td/*/text()',
            'firmware': '//td/*[text()="UPS Firmware Release"]/../following-sibling::td//td/*/text()',
            'agent_firmware': '//td/*[text()="UPS Agent Version"]/../following-sibling::td//td/*/text()',
        }
        info = {}
        info['manufacturer'] = 'Socomec'
        info['agent_type'] = 'NetVision'
        for k, xpath in xpaths.items():
            info[k] = html.xpath(xpath)[0]
        if info.get('agent_firmware'):
            m = re.search(r'v(\d\S+)(?:\s\(\S*\s*(\S+)\))', info['agent_firmware'])
            if m:
                info['agent_firmware'] = m.group(1)
                if m.group(2):
                    info['agent_serial'] = m.group(2)
        return info
