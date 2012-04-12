#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import sys
import subprocess

import settings

def main(dns_type):
    os.chdir(settings.named_path)

    # delete /etc/rndc.conf, or rndc will use it
    if os.path.isfile('/etc/rndc.conf'):
        os.unlink('/etc/rndc.conf')
    # debian
    if os.path.isfile('/etc/bind/rndc.conf'):
        os.unlink('/etc/bind/rndc.conf')

    # change user homedir and shell 
    # usermod  -d /home/named/ -s /bin/bash named
    code = subprocess.call(['/usr/sbin/usermod', '-d',
                            settings.named_path,
                            '-s', '/bin/bash',
                            settings.user])
    if code:
        sys.stderr.write('usermod failed, please login out user %s '
            'or stop name server\n' % settings.user)
        sys.exit(-1)

    # create rndc.key
    rndc_conf = '%s/rndc.key' % settings.named_path
    if not os.path.isfile(rndc_conf):
        code = subprocess.call('/usr/sbin/rndc-confgen -a -c %s' %
                               rndc_conf ,shell=True)
        if code:
            sys.stderr.write('error to create rndc.conf')

    # create ssh key
    ssh_dir = '%s/.ssh' % settings.named_path
    if not os.path.isdir(ssh_dir):
        os.mkdir(ssh_dir)
    ssh_key = '%s/id_rsa' % ssh_dir
    if dns_type == 'slave' and os.path.isfile(ssh_key)==False:
        sys.stderr.write('ssh key %s not found, please copy from master '
                         'dns server\n' % ssh_key)
        sys.exit(-1)
    if not os.path.isfile(ssh_key):
        code = subprocess.call("/usr/bin/ssh-keygen -f %s -N '' -q" %
                               ssh_key ,shell=True)
        if code:
            sys.stderr.write('error to create ssh_key')

    f=open(settings.sysconf, 'r+')

    nameconf = '%s/named.conf.%s' % (settings.named_path, dns_type)
    if settings.system == 'debian':
        uname = '-u bind '
    else:
        uname = ''
    try:
        content = f.read()
        if nameconf not in content:
            f.write('\n\n')
            f.write('OPTIONS="%s-c %s"\n' % (uname, nameconf))
    finally:
        f.close()

    subprocess.call('/bin/chown -R %s.%s %s'%(settings.user,
                    settings.user, settings.named_path), shell=True)

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'slave':
        main('slave')
    else:
        main('master')

