#-*- coding: utf-8 -*-

# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 PubYun, LLC.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""settings for GitNamed."""


import os
import sys
import platform

# IP of master name server
master_ip = '61.160.235.206'

# you can have multiple slave dns
# the value is the OS id (or family), e.g. centos/almalinux/rocky/rhel
# for the RHEL family, debian/ubuntu for the Debian family
slave_ips = {
            '61.160.235.203':'debian',
            '61.10.35.200':'centos',
           }

# key to transfer zone from master to slave
# dnssec-keygen -a hmac-md5 -b 128 -n HOST master2slave
transfer_key_body = 'MFnphERTs7gnX+XHcWoEOA=='

# some dynamic updated zones
dzones = {
            'dynupdate.org':'user1',
            'dynupdate.cn':'user2',
         }

named_path = os.path.dirname(os.path.abspath(
                             os.path.dirname(__file__)))

zones_path = os.path.join(named_path, 'zones')

# RHEL family: rhel/centos/fedora/almalinux/rocky/oracle ...
# Debian family: debian/ubuntu ...
rhel_family = ('rhel', 'redhat', 'centos', 'fedora', 'almalinux',
               'rocky', 'ol', 'oracle', 'scientific')
debian_family = ('debian', 'ubuntu')


def os_family(name):
    """Map an OS id/name to a family: 'rhel', 'debian' or None."""
    name = (name or '').lower()
    if name in rhel_family:
        return 'rhel'
    if name in debian_family:
        return 'debian'
    return None


def _os_release():
    """Read /etc/os-release as a dict, working on Python 3.6+."""
    try:
        # available since Python 3.10
        return platform.freedesktop_os_release()
    except AttributeError:
        pass
    except OSError:
        return {}
    data = {}
    for path in ('/etc/os-release', '/usr/lib/os-release'):
        try:
            with open(path) as fh:
                for line in fh:
                    line = line.strip()
                    if not line or line.startswith('#') or '=' not in line:
                        continue
                    key, value = line.split('=', 1)
                    data[key] = value.strip().strip('"').strip("'")
            return data
        except OSError:
            continue
    return data


def detect_system():
    """Detect the OS family of the local host from os-release."""
    info = _os_release()
    # ID is the primary id, ID_LIKE lists the families it derives from
    candidates = [info.get('ID', '')] + info.get('ID_LIKE', '').split()
    for candidate in candidates:
        family = os_family(candidate)
        if family:
            return family
    sys.stderr.write("can't determinate OS\n")
    sys.exit(-1)


system = detect_system()
if system == 'rhel':
    # uniform across the RHEL family (rhel/centos/fedora/almalinux/rocky...)
    user = 'named'
    sysconf = '/etc/sysconfig/named'
elif system == 'debian':
    user = 'bind'
    # /etc/default/bind9 was renamed to /etc/default/named in Debian 11
    # (bind9 9.16) / Ubuntu 22.04, so probe instead of hard-coding.
    sysconf = next((path for path in ('/etc/default/named',
                                      '/etc/default/bind9')
                    if os.path.isfile(path)), '/etc/default/named')

