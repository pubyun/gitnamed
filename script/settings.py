#-*- coding: utf-8 -*-

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

