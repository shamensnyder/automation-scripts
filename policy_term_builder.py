from netaddr import *
import jinja2
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
import sys
import argparse


'''
Builds a configration that adds to an existing term in a Juniper policy.
'''

jinja_template = '''policy-options {
    policy-statement export-routes-to-cogent {
        term {{ term }} {
            from {
                route-filter {{ prefix }} {% if '/24' in prefix %}exact; {% else %}upto /24;{% endif %}
            }
        }
    }
    policy-statement export-routes-to-he {
        term {{ term }} {
            from {
                route-filter {{ prefix }} {% if '/24' in prefix %}exact; {% else %}upto /24;{% endif %}
            }
        }
    }
    policy-statement export-routes-to-peer-public {
        term {{ term }} {
            from {
                route-filter {{ prefix }} {% if '/24' in prefix %}exact; {% else %}upto /24;{% endif %}
            }
        }
    }
    policy-statement export-routes-to-peer-google {
        term {{ term }} {
            from {
                route-filter {{ prefix }} {% if '/24' in prefix %}exact; {% else %}upto /24;{% endif %}
            }
        }
    }
}
'''

def main():

    parse = argparse.ArgumentParser()
    parse.add_argument("--prefix", type=str, required=True)
    parse.add_argument("--term", type=str, required=True)

    args = parse.parse_args()

    prefix = args.prefix
    term = args.term

    try:
        ip = IPNetwork(prefix)
        return ip
    except AddrFormatError:
        print('******************************************************\nInvaild IP Address. Check the IP entered and try again.\n******************************************************')
        sys.exit()

    template = jinja2.Template(jinja_template)
    out = template.render(prefix=prefix, term=term)

    print(out)

if __name__ == "__main__":
    main()
