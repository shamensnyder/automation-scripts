import argparse
import requests
import pprint
import jinja2

jinja_template = '''
protocols {
    bgp {
        {% for lan in lans %}
        group Peersv4 {
            neighbor {{ lan.ipaddr4 }} {
                description "{{ net.name }} : {{ lan.name }} :{% for poc in pocs %} {{ poc.email }} - {{ poc.phone }}{% endfor %}"
                family inet unicast prefix-limit maximum {{net.info_prefixes4}}
                family inet unicast prefix-limit teardown 80
                peer-as {{ lan.asn }}
                remove-private
                damping
                export [ export-peer-public final-policy ]
                import [ martian import-peer-public final-policy ]
            }
        }
        group Peersv6 {
            neighbor {{ lan.ipaddr6 }} {
                description "{{ net.name }} : {{ lan.name }} :{% for poc in pocs %} {{ poc.email }} - {{ poc.phone }}{% endfor %}"
                family inet6 unicast prefix-limit maximum {{net.info_prefixes6}}
                family inet6 unicast prefix-limit teardown 80
                peer-as {{ lan.asn }}
                remove-private
                damping
                import [ ipv6-route-filter import-peer-public-ipv6 final-policy ]
                export [ export-peer-public-ipv6 final-policy ]
            }
        {% endfor %}
        }
    }
}
'''

zito_ix_pop = {'dllstx': 1249, 'snjsca': 5, 'atlnga': 22, 'nycmny': 804}

def peeringdb_query(asn):
    r = requests.get(
        "https://www.peeringdb.com/api/net?asn={}&depth=2".format(asn))
    return r.json()['data'][0]

def main():
    parse = argparse.ArgumentParser()
    parse.add_argument("--asn", type=int, required=True)
    parse.add_argument("--ixcli", type=str, required=True)
    args = parse.parse_args()

    data = peeringdb_query(args.asn)

    lans = []
    for lan in data['netixlan_set']:
        if lan['ix_id'] == zito_ix_pop[args.ixcli]:
            lans.append(lan)

    pocs = []
    for poc in data['poc_set']:
        if poc['role'] == 'NOC':
            pocs.append(poc)

    template = jinja2.Template(jinja_template)
    out = template.render(net=data, lans=lans, pocs=pocs)

    print(out)

if __name__ == "__main__":
    main()
