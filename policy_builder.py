from netaddr import *
import jinja2
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
import sys


'''
Builds a configration that adds to an existing term in a Juniper policy.
'''

jinja_template = '''policy-options {
    policy-statement {{ policy_name }} {
        term {{ existing_term }} {
            from {
                route-filter {{ new_prefix }} {{% if '/24' in cidr %}} exact; {{% else %}}upto /24;
            }
        }
    }
}
'''
            
