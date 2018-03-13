import argparse
import requests
import pprint
import jinja2
from netaddr import *
from time import sleep
import sys

"""
Uses argparse to build a configuration using Jinja2 and POST IP or alert user that IP is already in use in Netbox.
Variables that are mandatory are '--clli' and '--mgmt'. Optional variable '--loc'

clli = hostname
mgmt = IP (used for IP of device, trap source, and default gateway)
loc = Locattion (used for SNMP location)
"""


jinja_template='''
system {
    host-name as0-{{ hostname }};
    domain-name zitomedia.net;
    domain-search zitomedia.net;
    time-zone America/New_York;
    authentication-order [ radius password ];
    root-authentication {
        encrypted-password "$1$1dIQmpo0$C3oAVhoojM/NaTm6/p6vz1"; ## SECRET-DATA
    }
    name-server {
        74.81.99.1;
        74.81.99.2;
    }
    radius-server {
        74.81.97.77 {
            port 1812;
            secret "$9$ZlDqmFn/01E/9pBIRyr24oaikFn/pO1NdGjqmzFSrlKWXaJDHm5LxUjq.zFcylMWx7-VoZUsYDkPT/9X7NVYok.5n9ARh"; ## SECRET-DATA
        }
    }
    login {
        class demigod {
            idle-timeout 20;
            permissions all;
        }
        class network {
            idle-timeout 20;
            permissions [ clear interface network reset trace view ];
        }
        class observer {
            idle-timeout 5;
            permissions [ interface network view ];
        }
        class rancid {
            idle-timeout 5;
            permissions [ admin firewall interface network routing secret snmp system view ];
        }
        class view {
            idle-timeout 5;
            permissions [ interface network system view view-configuration ];
            allow-commands "request support *";
        }
        user cgist {
            uid 2002;
            class super-user;
            authentication {
                encrypted-password "$1$n7hubAIV$SJifmz0StM0.nX2mVvCug/"; ## SECRET-DATA
            }
        }
        user dbernardi {
            uid 2003;
            class super-user;
            authentication {
                encrypted-password "$1$QQglge8i$7rOLCDvYV68wqD5y6FdrC/"; ## SECRET-DATA
            }
        }
        user demigod {
            full-name "Radius Superuser Pseudouser";
            uid 2015;
            class demigod;
        }
        user local {
            full-name "Local Superuser";
            uid 2016;
            class demigod;
            authentication {
                encrypted-password "$1$4KEbtMia$VX8DC3LcGQ7lRoQs5iG1c/"; ## SECRET-DATA
            }
        }
        user network {
            full-name "Radius Network Pseudouser";
            uid 2017;
            class network;
        }
        user rancid {
            uid 116;
            class rancid;
            authentication {
                encrypted-password "$1$iOJT1Blf$kG5Omx.NwMCZclAi9RjY4/"; ## SECRET-DATA
            }
        }
        user view {
            full-name "Radius View Pseudouser";
            uid 2018;
            class view;
        }
    }
    services {
        ftp;
        ssh {
            root-login allow;
            connection-limit 10;
            rate-limit 4;
        }
    }
    syslog {
        user * {
            any emergency;
        }
        file messages {
            any any;
            authorization info;
        }
        file interactive-commands {
            interactive-commands any;
        }
    }
    ntp {
        server 74.81.99.5 version 4;
    }
}
chassis {
    redundancy {
        graceful-switchover;
    }
    aggregated-devices {
        ethernet {
            device-count 25;
        }
    }
    alarm {
        management-ethernet {
            link-down ignore;
        }
    }
}
interfaces {
    vlan {
        unit 4010 {
            family inet {
                address {{ management_ip }};
            }
        }
    }
}
snmp {
    location "{{ location }}";
    contact "<noc@zitobusiness.com>";
    filter-duplicates;
    community z1t0-n3tw0rks {
        authorization read-only;
        clients {
            74.81.97.75/32;
            74.81.97.87/32;
            74.81.96.0/23;
        }
    }
    trap-options {
        source-address {{ trap_ip }};
    }
    trap-group snmp-trap {
        version v2;
        categories {
            authentication;
            chassis;
            link;
            routing;
            startup;
            rmon-alarm;
            vrrp-events;
            configuration;
            services;
        }
        targets {
            74.81.97.87;
            74.81.97.102;
        }
    }
}
routing-options {
    static {
        route 0.0.0.0/0 next-hop {{ default_gw }};
    }
}
protocols {
    lldp {
        interface all;
    }
    lldp-med {
        interface all;
    }
}
policy-options {
    prefix-list trusted {
        67.58.160.0/23;
        71.245.181.4/32;
        74.81.96.0/23;
        173.246.224.0/23;
    }
    prefix-list snmp-nms {
        74.81.97.64/26;
    }
}
firewall {
    family inet {
        filter lo0 {
            term allow-tcp {
                then accept;
            }
            term allow-icmp {
                from {
                    protocol icmp;
                }
                then {
                    policer small-bw-limit;
                    log;
                    accept;
                }
            }
            term allow-tracert {
                from {
                    protocol udp;
                    destination-port 33434-33523;
                }
                then accept;
            }
            inactive: term allow-bgp {
                from {
                    source-prefix-list {
                        bgp-peers;
                    }
                    protocol tcp;
                    destination-port bgp;
                }
                then accept;
            }
            term allow-snmp {
                from {
                    source-prefix-list {
                        snmp-nms;
                        trusted;
                    }
                    protocol udp;
                    destination-port snmp;
                }
                then accept;
            }
            term deny-all {
                then {
                    discard;
                }
            }
        }
    }
    policer small-bw-limit {
        if-exceeding {
            bandwidth-limit 10m;
            burst-size-limit 15k;
        }
        then discard;
    }
}
ethernet-switching-options {
    dot1q-tunneling {
        ether-type 0x8100;
    }
    storm-control {
        interface all;
    }
}
vlans {
    mgmt {
        vlan-id 4010;
        l3-interface vlan.4010;
    }
}
'''

def main():

    url = 'http://netbox.zitomedia.net/api/ipam/ip-addresses/'

    parse = argparse.ArgumentParser()
    parse.add_argument("--clli", type=str, required=True)
    parse.add_argument("--mgmt", type=str, required=True)
    parse.add_argument("--loc", type=str, required=False)

    args = parse.parse_args()

    hostname = args.clli
    management_ip = args.mgmt
    location = args.loc

    ip = IPNetwork(management_ip)
    querystring = {"q":ip.ip}
    trap_ip = IPAddress(ip)
    default_gw = ip.network + 1

    response = requests.request("GET", url, params=querystring)
    jdata = response.json()

    headers = {
        'Authorization': "Token 7f928d324c584fff98e21a9eb8ff1bf3fd45aff9" ##Bogus Token Used ;)
        }
    payload = {
        'description': 'as0-' + hostname,
        'address': str(ip.ip)
        }

    if jdata['count'] == 0 :
        print("*" * 60 + "\nIP Address not reserved in Netbox, POSTing...\n" + "*" * 60)
        post_response = requests.post(url, headers=headers, data=payload)
    elif jdata['count'] > 0 and jdata['results'][0]['address'][:-3] == str(ip.ip) :
        netboxDescription = jdata['results'][0]['description']
        print("*" * 60 + "\nWARNING! Selected IP Address is already reserved in Netbox as " + netboxDescription + "\n" + "*" * 60)

    sleep(2)
    template = jinja2.Template(jinja_template)
    out = template.render(hostname=hostname, management_ip=management_ip, trap_ip=trap_ip, default_gw=default_gw, location=location)

    print('Saving configuration...')
    f = open('/var/www/html/as0-' + hostname + '-base.txt', 'w')
    f.write(out)
    f.close

if __name__ == "__main__":
    main()
