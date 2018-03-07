import argparse
import requests
import pprint
import jinja2
from netaddr import *
from time import sleep
import sys

jinja_template = '''hostname {{ hostname }}
username admin privilege 15 password encrypted wersdtfyguhiji
!
vlan {{ vlan }}
 name vlan-{{ vlan }}
!
vlan 4010
 name vlan-4010
!
snmp-server host Observium-alerting
 no shutdown
 host a.b.c.d 162 informs
 version v2 z1t0-n3tw0rks
 traps system warmstart coldstart
!
ip route 0.0.0.0 0.0.0.0 {{ default_gw }}
ntp
aaa authentication login ssh radius
aaa authentication login http radius local
radius-server attribute 32 tmc-3306
radius-server host a.b.c.d timeout 3 retransmit 1 key qw456yuji
!
interface GigabitEthernet 1/1
 switchport access vlan {{ vlan }}
 description place-holder
!
interface GigabitEthernet 1/2
!
interface GigabitEthernet 1/3
!
interface GigabitEthernet 1/4
!
interface GigabitEthernet 1/5
 switchport trunk allowed vlan {{ vlan }},4010
 switchport mode trunk
 description as0-{{ clli }} : ge-x/x/x : :
!
interface GigabitEthernet 1/6
!
interface GigabitEthernet 1/7
!
interface GigabitEthernet 1/8
!
interface vlan 4010
 ip address {{ mgmt }} {{ subnetmask }}
!
line console 0
!
line vty 0
!
line vty 1
!
line vty 2
!
line vty 3
!
line vty 4
!
line vty 5
!
line vty 6
!
line vty 7
!
line vty 8
!
line vty 9
!
line vty 10
!
line vty 11
!
line vty 12
!
line vty 13
!
line vty 14
!
line vty 15
!
end
'''


def main():

    url = 'http://netbox.zitomedia.net/api/ipam/ip-addresses/'
  
    parse = argparse.ArgumentParser()
    parse.add_argument("--clli", type=str, required=True)
    parse.add_argument("--vlan", type=str, required=False)
    parse.add_argument("--mgmt", type=str, required=True)

    args = parse.parse_args()

    hostname = args.clli
    vlan = args.vlan
    mgmt = args.mgmt


    mgmt = IPNetwork(mgmt)
    querystring = {"q":mgmt.ip}
    default_gw = mgmt.network + 1
    clli = hostname[4:10]
    subnetmask = mgmt.netmask
    payload_ip = mgmt
    mgmt = mgmt.ip


    response = requests.request("GET", url, params=querystring)
    jdata = response.json()


    headers = {
        'Authorization': "Token Your Token Here" # Change token for your enviroment
        }
    payload = {
        'description': hostname,
        'address': str(payload_ip)
        }

    if jdata['count'] == 0 :
        print("**********************************************************************\nIP Address not reserved in Netbox, POSTing...\n**********************************************************************")
        post_response = requests.post(url, headers=headers, data=payload)
    elif jdata['count'] > 0 and jdata['results'][0]['address'][:-3] == str(mgmt) :
        netboxDescription = jdata['results'][0]['description']
        print("**********************************************************************\nWARNING! Selected IP Address is already reserved in Netbox as " + netboxDescription + "\n**********************************************************************")

    sleep(2)
    template = jinja2.Template(jinja_template)
    out = template.render(hostname=hostname, mgmt=mgmt, default_gw=default_gw, clli=clli, vlan=vlan, subnetmask=subnetmask)

    #print('Saving configuration...')
    #f = open('/Users/ssnyder/Google Drive/Configurations/' + hostname + '-base.txt', 'w')
    #f.write(out)
    #f.close

    print(out)

if __name__ == "__main__":
    main()
