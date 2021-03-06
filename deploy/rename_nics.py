import os
import sys
import yaml


def exec_cmd(cmd):
    print cmd
    os.system(cmd)


def rename_nics(dha_info, rsa_file, compass_ip, os_version):
    for host in dha_info['hosts']:
        host_name = host['name']
        interfaces = host.get('interfaces')
        if interfaces:
            for interface in interfaces:
                nic_name = interface.keys()[0]
                mac = interface.values()[0]

                exec_cmd("ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
                          -i %s root@%s \
                          'cobbler system edit --name=%s --interface=%s --mac=%s --static=1'"   # noqa
                         % (rsa_file, compass_ip, host_name, nic_name, mac))   # noqa

    exec_cmd("ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
              -i %s root@%s \
              'cobbler sync'" % (rsa_file, compass_ip))

if __name__ == "__main__":
    assert(len(sys.argv) == 5)
    rename_nics(
        yaml.load(
            open(
                sys.argv[1])),
        sys.argv[2],
        sys.argv[3],
        sys.argv[4])
