from netaddr import *
import jinja2
#from jnpr.junos import Device
#from jnpr.junos.utils.config import Config
import sys
import argparse


'''
Builds a configration that adds to an existing term in a Juniper policy.
'''

'''policy-options {
    policy-statement cogent-export-routes-to-transit {
        term {{ term }} {
            from {
                community [ customer customer-residential ]
                {% for prefix in prefixes %}route-filter {{ prefix }} {% if '/24' in prefix %}exact; {% else %}upto /24;{% endif %}
                {% endfor %}}
            then next policy;
            }
        }
    policy-statement export-routes-to-transit {
        term {{ term }} {
            from {
                community [ customer customer-residential ]
                {% for prefix in prefixes %}route-filter {{ prefix }} {% if '/24' in prefix %}exact; {% else %}upto /24;{% endif %}
                {% endfor %}}
            then next policy;
            }
        }
    policy-statement export-peer-public {
        term {{ term }} {
            from {
                community [ customer customer-residential ]
                {% for prefix in prefixes %}route-filter {{ prefix }} {% if '/24' in prefix %}exact; {% else %}upto /24;{% endif %}
                {% endfor %}}
            then next policy;
            }
        }
    policy-statement export-peer-private {
        term {{ term }} {
            from {
                community [ customer customer-residential ]
                {% for prefix in prefixes %}route-filter {{ prefix }} {% if '/24' in prefix %}exact; {% else %}upto /24;{% endif %}
                {% endfor %}}
            then next policy;
            }
        }
    policy-statement netflix-export-bgp {
        term {{ term }} {
            from {
                community [ customer customer-residential ]
                {% for prefix in prefixes %}route-filter {{ prefix }} {% if '/24' in prefix %}exact; {% else %}upto /24;{% endif %}
                {% endfor %}}
            then next policy;
            }
        }
    policy-statement export-peer-public-google {
        term {{ term }} {
            from {
                community [ customer customer-residential ]
                {% for prefix in prefixes %}route-filter {{ prefix }} {% if '/24' in prefix %}exact; {% else %}upto /24;{% endif %}
                {% endfor %}}
            then next policy;
            }
        }
    }
insert policy-options policy-statement cogent-export-routes-to-transit term {{ term }} before term deny-all
insert policy-options policy-statement export-routes-to-transit term {{ term }} before term deny-all
insert policy-options policy-statement export-peer-public term {{ term }} before term deny-all
insert policy-options policy-statement export-peer-private term {{ term }} before term deny-all
insert policy-options policy-statement netflix-export-bgp term {{ term }} before term deny-all
insert policy-options policy-statement export-peer-public-google term {{ term }} before term deny-all
'''

def main():

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

    print(out)


if __name__ == "__main__":
    main()
