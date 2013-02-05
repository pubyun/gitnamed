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

system = platform.dist()[0]
if system == 'centos':
    user = 'named'
    sysconf = '/etc/sysconfig/named'
elif system == 'debian':
    user = 'bind'
    sysconf = '/etc/default/bind9'
else:
    sys.stderr.write("can't determinate OS\n")
    sys.exit(-1)

