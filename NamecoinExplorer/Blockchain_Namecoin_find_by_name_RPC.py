# -*- coding: utf8 -*-
__author__ = 'sai'

import requests
import json
import ipaddress
import re
import collections
import datetime
import concurrent.futures
from requests.auth import HTTPBasicAuth
import urllib3
urllib3.disable_warnings()

try:
    from ontology import (
        Task, Header, HeaderCollection, Utils, Field, ValueType, SchemaLink, SchemaObject, Condition, Operations, Macro,
        MacroCollection, Schema, EnterParamCollection, SchemaCollection, GraphMappingFlags, BinaryType, Constants,
        Attributes, IP, Domain, IPToDomain)

except ImportError as ontology_exception:
    print('...missing or invalid ontology')
    raise ontology_exception


def return_ip(text):
    result = []
    ipPattern = r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})'
    ipaddress_subtmp = re.findall(ipPattern, text)
    if ipaddress_subtmp:
        for ip in ipaddress_subtmp:
            try:
                _ip = ipaddress.ip_address(ip.strip())
                result.append(str(_ip))
            except:
                pass
    return result


def not_empty(field: Field):
    return Condition(field, Operations.NotEqual, '')


def get_block_hashs(hashs, server, user, password):
    headers = {'content-type':'text/plain'}
    if isinstance(hashs, collections.Iterable):
        v = hashs
    else:
        v = [hashs]
    payload = {
        "method": "getblockhash",
        "params": v,
        "jsonrpc": "1.0",
        "id": "curltest"
    }
    response = requests.post(
        server, data=json.dumps(payload), headers=headers, auth=HTTPBasicAuth(user, password))
    if response.ok:
        data = response.json()
        if 'result' in data:
            return data['result']


def get_block_info(hashs, server):
    headers = {'content-type':'text/plain'}
    if isinstance(hashs, collections.Iterable) and not isinstance(hashs, str):
        v = hashs
    else:
        v = [hashs]
    # v = [hashs]
    payload = {
        "method": "getblock",
        "params": v,
        "jsonrpc": "1.0",
        "id": "curltest"
    }

    response = requests.post(
        server, data=json.dumps(payload), headers=headers, auth=HTTPBasicAuth("user", "moscow"))

    if response.ok:
        data = response.json()

        if 'result' in data:
            return data['result']


def name_history_one(domain, value, server, user, password):

    def parse_record(row):
        tmp_result = {"domain":domain}
        tmp_result['ips'] = []
        if 'name' in row.keys():
            tmp_result['namecoin_domain'] = row['name']
        if 'value' in row.keys():
            try:
                v = json.loads(row['value'].replace('\n',' ').replace('\t',' '))
                if 'ip' in v.keys():
                    if isinstance(v['ip'], list):
                        for ip in v['ip']:
                            tmp_result['ips'].append(ip)
                    elif isinstance(v['ip'], str):
                        ips = return_ip(v['ip'])
                        tmp_result['ips'].extend(ips)
                else:
                    ips = return_ip(row['value'])
                    tmp_result['ips'].extend(ips)

            except:
                ips = return_ip(row['value'])
                tmp_result['ips'].extend(ips)
        if 'txid' in row.keys():
            tmp_result['txid'] = row['txid']
        _keys = ['address', 'height', 'expired', 'expires_in']
        for k in _keys:
            if k in row.keys():
                tmp_result[k] = row[k]
        if 'expired' in tmp_result.keys():
            tmp_result['expired'] = not tmp_result['expired']
        timeblock = None
        hash_block = None
        if 'height' in tmp_result:
            h = get_block_hashs(tmp_result['height'], server, user, password)
            info = get_block_info(h, server)
            try:
                timeblock = datetime.datetime.utcfromtimestamp(info['time'])
                hash_block = info['hash']
            except:
                pass
        tmp_result['date_time'] = timeblock
        tmp_result['hash_block'] = hash_block
        return tmp_result

    headers = {'content-type':'text/plain'}

    payload = {
        "method": "name_history",
        "params": [value],
        "jsonrpc": "1.0",
        "id": "curltest"
    }
    try:
        response = requests.post(
            server, data=json.dumps(payload), headers=headers, auth=HTTPBasicAuth(user, password))
        check = response.ok
        data = response.json()
    except Exception as e:
        check = False
        data = None
        data_errors = str(e)
        print(data_errors)

    if check and data:
        try:
            if 'result' in data:
                for block in data['result']:
                    _tmp_row = parse_record(block)
                    row = _tmp_row.copy()
                    row.pop('ips')
                    for _ip in _tmp_row['ips']:
                        row['ip'] = _ip
                        yield row
        except:
            print('high level errors...')
    else:
        print('errors with service...:{}, {}'.format(check, data))


def return_namecoin(namedomain):
    if namedomain.endswith(".bit"):
        return {'domain':namedomain, 'namecoin_domain': f"d/{namedomain[:-4]}"}
    elif namedomain.startswith('d/'):
        return {'domain':namedomain[2:]+'.bit', 'namecoin_domain':namedomain}


def return_massive_about_domains(domains, server, threads, lg, user, password):
    namecoins = map(return_namecoin, domains)
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        future_rows = {executor.submit(name_history_one, namecoin['domain'], namecoin['namecoin_domain'],
                                       server, user, password):
                           namecoin for namecoin in namecoins}
        for future in concurrent.futures.as_completed(future_rows):
            domain_try = future_rows[future]
            result = future.result()
            if result:
                for line in result:
                    yield line


class NamecoinDomainExplorer(metaclass=Header):
    display_name = 'Namecoin Explorer'
    date_time = Field('Date and time Block', ValueType.Datetime)
    domain = Field('Domain', ValueType.String)
    namecoin_domain = Field('Namecoin name', ValueType.String)
    ip = Field('ip', ValueType.String)
    Netblock = Field('Netblock', ValueType.String)
    expired = Field('Status', ValueType.Boolean)
    address = Field('address', ValueType.String)
    height = Field('height', ValueType.Integer)
    hash_block = Field('hash_block', ValueType.String)
    txid = Field('txid', ValueType.String)


class NamecoinDomainIP(metaclass=Schema):
    name = 'Namecoin schema: Domain and IP'
    Header = NamecoinDomainExplorer

    SchemaIP = SchemaObject(IP, mapping={IP.IP: Header.ip})
    SchemaDomain = SchemaObject(Domain, mapping={Domain.Domain: Header.domain})

    SchemaIPToDomain = IPToDomain.between(
        SchemaIP, SchemaDomain,
        mapping={IPToDomain.Resolved: Header.date_time},
        conditions=[not_empty(Header.domain), not_empty(Header.ip)])


class NamecoinHistoryDomainIPRPC(Task):

    def __init__(self):
        super().__init__()
        self.info, self.error, self.result, self.api, self.api_key = [None] * 5

    def get_id(self):
        return '7ab3d285-078d-4b95-a7ae-3bfbee6cc818'

    def get_display_name(self):
        return 'Explore Namecoin names(RPC server)'

    def get_category(self):
        return "Blockchain:\tNamecoin"

    def get_description(self):
        return 'Return history Namecoin name\n\nEnter parameters "d/example or example.bit'

    def get_weight_function(self):
        return 'domains'

    def get_headers(self):
        return HeaderCollection(NamecoinDomainExplorer)

    def get_schemas(self):
        return SchemaCollection(NamecoinDomainIP)

    def get_graph_macros(self):
        return MacroCollection(
            Macro(name='Namecoin:\tExplore domains(RPC)', mapping_flags=[GraphMappingFlags.Completely],
                  schemas=[NamecoinDomainIP]))

    def get_enter_params(self):
        ep_coll = EnterParamCollection()
        ep_coll.add_enter_param('domains', 'Namecoin domain', ValueType.String, is_array=True, required=True,
                                value_sources=[Attributes.System.Domain],
                                description='Namecoin domain, e.g.:\nd/example'
                                            '\nexample.bit')
        ep_coll.add_enter_param('server', 'host with Namecoind(RPC-JSON)', ValueType.String, is_array=False, required=True,
                                predefined_values=["http://68.183.0.119:8336"],
                                default_value="http://68.183.0.119:8336")
        ep_coll.add_enter_param('threads', 'Max threads', ValueType.Integer, is_array=False, required=True,
                                predefined_values=[4,8], default_value=4)
        ep_coll.add_enter_param('userRPC', 'username for RPC', ValueType.String, is_array=False, required=True,
                                default_value="user")
        ep_coll.add_enter_param('passwordRPC', 'password for RPC', ValueType.String, is_array=False, required=True,
                                default_value="moscow")

        return ep_coll

    def execute(self, enter_params, result_writer, log_writer, temp_dir=None):

        server = enter_params.server
        domains = enter_params.domains
        user = enter_params.userRPC
        password = enter_params.passwordRPC

        log_writer.info("Number of Namecoins:{}".format(len(domains)))
        threadsmax = enter_params.threads
        result_lines = return_massive_about_domains(domains, server, threadsmax, log_writer, user, password)
        i = 1
        for line in sorted(result_lines,  key=lambda line: line['date_time']):
            log_writer.info('ready:{}.\t{}'.format(i, line['domain']))
            fields_table = NamecoinDomainExplorer.get_fields()
            tmp = NamecoinDomainExplorer.create_empty()
            for field in fields_table:
                if field in line:
                    tmp[fields_table[field]] = line[field]
            result_writer.write_line(tmp, header_class=NamecoinDomainExplorer)
            i += 1

if __name__ == '__main__':
    DEBUG = True

    class EnterParamsFake:
        domains = ['d/microsoft-downloads',
                   'porshegate.bit',
                   'primecinema.bit',
                   'qofeticzapcjbkxm.bit'
                   ]
        server = "http://68.183.0.119:8336"
        userRPC = "user"
        passwordRPC = "moscow"
        threads = 4

    class WriterFake:
        @classmethod
        # ResultWriter method
        def write_line(cls, values, header_class=None):
            print({f.display_name: v for f, v in values.items()})

        @classmethod
        # LogWriter method
        def info(cls, message, *args):
            print(message, *args)

        @classmethod
        # LogWriter method
        def error(cls, message, *args):
            print(message, *args)

    NamecoinHistoryDomainIPRPC().execute(EnterParamsFake, WriterFake, WriterFake, None)