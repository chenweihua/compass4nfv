import yaml
import netaddr
import os
import log as logging

LOG = logging.getLogger("net-init")
config_path = os.path.join(os.path.dirname(__file__), "network.cfg")
#from socket import AF_INET
#from pyroute2 import IPRoute
#from pyroute2 import IPRouteRequest

#ip = IPRoute()
def setup_bondings(bond_mappings):
    print bond_mappings

def add_vlan_link(interface, ifname, vlan_id):
    LOG.info("add_vlan_link enter")
    #idx = ip.link_lookup(ifname=interface)[0]
    #ip.link_create(ifname=ifname,
    #               kind="vlan",
    #               vlan_id=vlan_id,
    #               link=idx)
    cmd = "ip link add link %s name %s type vlan id %s; " % (ifname, interface, vlan_id)
    cmd += "ip link set %s up; ip link set %s up" % (interface, ifname)
    LOG.info("add_vlan_link: cmd=%s" % cmd)
    os.system(cmd)

def add_ovs_port(ovs_br, ifname, vlan_id=None):
    LOG.info("add_ovs_port enter")
    cmd = "ovs-vsctl --may-exist add-port %s %s" % (ovs_br, ifname)
    if vlan_id:
        cmd += " tag=%s" % vlan_id
    cmd += " -- set Interface %s type=internal;" % ifname
    cmd += "ip link set %s up;" % ifname
    LOG.info("add_ovs_port: cmd=%s" % cmd)
    os.system(cmd)

def setup_intfs(sys_intf_mappings):
    LOG.info("setup_intfs enter")
    for intf_name, intf_info in sys_intf_mappings.items():
        if intf_info["type"] == "vlan":
            add_vlan_link(intf_name, intf_info["interface"], intf_info["vlan_tag"])
        elif intf_info["type"] == "ovs":
            add_ovs_port(intf_info["interface"], intf_name, vlan_id=intf_info.get("vlan_tag"))
        else:
            pass

def setup_ips(ip_settings, sys_intf_mappings):
    LOG.info("setup_ips enter")
    for intf_info in ip_settings.values():
        network = netaddr.IPNetwork(intf_info["cidr"])
        if sys_intf_mappings[intf_info["name"]]["type"] == "ovs":
            intf_name = intf_info["name"]
        else:
            intf_name = intf_info["alias"]
        cmd = "ip addr add %s/%s brd %s dev %s;" \
              % (intf_info["ip"], intf_info["netmask"], str(network.broadcast),intf_name)
        if "gw" in intf_info:
            cmd += "ip route add default via %s dev %s" % (intf_info["gw"], intf_name)
        LOG.info("setup_ips: cmd=%s" % cmd)
        os.system(cmd)
        #idx = ip.link_lookup(ifname=intf_name)[0]
        #ip.addr('add',
        #        index=idx,
        #        address=intf_info["ip"],
        #        broadcast=str(network.broadcast),
        #        prefixlen=intf_info["netmask"])

def main(config):
    setup_bondings(config["bond_mappings"])
    setup_intfs(config["sys_intf_mappings"])
    setup_ips(config["ip_settings"], config["sys_intf_mappings"])

if __name__ == "__main__":
    os.system("service openvswitch-switch status|| service openvswitch-switch start")
    config = yaml.load(open(config_path))
    main(config)