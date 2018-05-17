from netaddr import *
import jinja2
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
import sys
import argparse

'''
Builds a configration that adds to an existing policy and term in a Juniper policy.
'''

jinja_template='''{% for prefix in prefixes %}set policy-options policy-statement cogent-export-routes-to-transit term {{ term }} from route-filter {{ prefix }} {% if '/24' in prefix %}exact; {% else %}upto /24{% endif %}
{% endfor -%}
{% for prefix in prefixes %}set policy-options policy-statement he-export-routes-to-transit term {{ term }} from route-filter {{ prefix }} {% if '/24' in prefix %}exact; {% else %}upto /24{% endif %}
{% endfor -%}
{% for prefix in prefixes %}set policy-options policy-statement export-peer-public term {{ term }} from route-filter {{ prefix }} {% if '/24' in prefix %}exact; {% else %}upto /24{% endif %}
{% endfor -%}
{% for prefix in prefixes %}set policy-options policy-statement netflix-export-bgp term {{ term }} from route-filter {{ prefix }} {% if '/24' in prefix %}exact; {% else %}upto /24{% endif %}
{% endfor -%}
{% for prefix in prefixes %}set policy-options policy-statement export-peer-public-google term {{ term }} from route-filter {{ prefix }} {% if '/24' in prefix %}exact; {% else %}upto /24{% endif %}
{% endfor -%}
'''

def main():
    dev = Device(host='172.30.249.150', user='lab', password='lab123')
    cu = Config(dev)
    parse = argparse.ArgumentParser()
    parse.add_argument("--prefix", type=str, required=True)
    parse.add_argument("--term", type=str, required=True)

    args = parse.parse_args()
    term = args.term
    prefixes = []
    for prefix in args.prefix :
        prefixes.append(prefix)

    prefixes1 = ''.join(prefixes)
    #print(prefixes1)

    prefixes = prefixes1.split(',')
    #print(prefixes)

    try:
        for cidr in prefixes:
            ip = IPNetwork(cidr)
    except AddrFormatError:
        print("Invalid IPv4 address format. Please check the prefix and try again.")
        sys.exit()

    template = jinja2.Template(jinja_template)
    out = template.render(prefixes=prefixes, term=term)

    #print(out)

    confbuild = out.split('\n')
    #print(confbuild)
    print("Opening connection to device...")
    dev.open()
    print("\n\n\n")
    print("Applying configuration...")
    cu.lock()
    for line in confbuild:
        cu.load(line, format='set')
    diff = cu.pdiff()
    print(diff)
    while True:
        comchange = input("\nDo you acceept the changes?")
        if comchange == 'yes':
            cu.commit(comment='Automation Script')
            cu.unlock()
            dev.close()
            break
        elif comchange == 'no':
            cu.rollback()
            cu.unlock()
            dev.close()
            break


if __name__ == "__main__":
    main()
