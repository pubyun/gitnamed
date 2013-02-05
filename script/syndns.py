#!/usr/bin/env python
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

"""Sync script for GitNamed."""

import os
import sys
import subprocess

import settings

named_conf_master = os.path.join(settings.named_path, 'named.conf.master')
named_conf_slave = os.path.join(settings.named_path, 'named.conf.slave')

transfer_key_name = 'master2slave'

transfer_key = u'''
key %s {
    algorithm hmac-md5;
    secret "%s";
};

''' % (transfer_key_name, settings.transfer_key_body)

nameconf_master = u'''zone "%s" {
    type master;
    file "zones/%s";
    %s;
    allow-transfer {
        %s;
    };
%s};
'''

nameconf_slave = u'''zone "%s" {
    type slave;
    file "zones/%s";
    masters {
        %s;
    };
};
'''

dyndns_update = u'''    allow-update {key %s; };\n'''

all_slave = ' '.join('%s;' % slave_ip
                     for (slave_ip, system) in settings.slave_ips.items())

notify_str = 'also-notify {%s}' % all_slave


def get_user(system):
    if system == 'centos':
        return 'named'
    elif system == 'debian':
        return 'bind'
    else:
        sys.stderr.write("can't determinate OS\n")
        sys.exit(-1)

def is_file(name):
    return os.path.isfile(os.path.join(settings.zones_path, name))

def get_master(z):
    transfer_key = 'key %s' % transfer_key_name;
    if z in settings.dzones:
        key = settings.dzones[z]
        dstring = dyndns_update % key
        transfer_key += '; key %s' % key
    else:
        dstring = ''
    return nameconf_master%(z, z, notify_str, transfer_key, dstring)

def reload_slave(slave_ip, system):
    user = get_user(system)
    sys.stdout.write("reloading %s\n" % slave_ip)
    # copy named.conf.master to slave
    slave_arg = '%s@%s:%s' % (user, slave_ip, settings.named_path)
    code = subprocess.call(['/usr/bin/scp', named_conf_slave,
                            slave_arg])
    if code:
        sys.stderr.write('copy %s to slave %s failed\n' %
                (named_conf_slave, slave_ip))
        sys.exit(-1)

    # reload slave dns
    rndc_conf = '%s/rndc.key' % settings.named_path
    code = subprocess.call('/usr/bin/ssh %s@%s '
                            '/usr/sbin/rndc -k %s -s localhost reload' %
                            (user, slave_ip, rndc_conf), shell=True)
    if code:
        sys.stderr.write('reload slave name server %s failed\n' % slave_ip)
        sys.exit(-1)


def main():

    os.chdir(settings.named_path)

    # pull code from git repo
    code = subprocess.call('/usr/bin/git pull hub master', shell=True)
    if code:
        sys.stderr.write('git pull code failed\n')

    # get all zones, exclude journal file
    zones = [f for f in os.listdir(settings.zones_path)
                 if is_file(f) and not f.endswith('.jnl')]

    # create named.conf.master
    with open(named_conf_master, 'w') as f:
        f.write('include "%s/named.conf";\n\n' % settings.named_path)
        f.write(transfer_key)
        f.write('\n'.join([get_master(z) for z in zones]))

    # create named.conf.slave
    with open(named_conf_slave, 'w') as f:
        f.write('include "%s/named.conf";\n\n' % settings.named_path)
        f.write(transfer_key)
        f.write('server %s { keys %s; };\n\n' %
                (settings.master_ip, transfer_key_name))
        f.write('\n'.join([nameconf_slave%(z, z,
            settings.master_ip) for z in zones]))

    # reload master dns
    rndc_conf = '%s/rndc.key' % settings.named_path
    code = subprocess.call('/usr/sbin/rndc -k %s -s localhost reload' %
                           rndc_conf, shell=True)
    if code:
        sys.stderr.write('reload master name server failed\n')
        sys.exit(-1)

    for (slave_ip,system) in settings.slave_ips.items():
        reload_slave(slave_ip, system)

if __name__ == '__main__':
    main()

