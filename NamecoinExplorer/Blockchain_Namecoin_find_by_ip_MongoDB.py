# -*- coding: utf8 -*-
__author__ = 'sai'

import time
from pymongo import MongoClient
import ipaddress

try:
    from ontology import (
        Task, Header, HeaderCollection, Utils, Field, ValueType, SchemaLink, SchemaObject, Condition, Operations, Macro,
        MacroCollection, Schema, EnterParamCollection, SchemaCollection, GraphMappingFlags, BinaryType, Constants,
        Attributes, IP, Domain, IPToDomain)

except ImportError as ontology_exception:
    print('...missing or invalid ontology')
    raise ontology_exception


def init_connect_to_mongodb(ip, port, dbname, username=None, password=None):
    """
    :param ip:  ip server MongoDB
    :param port: 27017
    :return: True, if connected, and set value mongoclient - MongoClient
    """
    if username and password:
        connect_string_to = 'mongodb://{}:{}@{}:{}/{}'.format(username, password, ip, port, dbname)
    else:
        connect_string_to = 'mongodb://{}:{}/{}'.format(ip, port, dbname)

    check = False
    count_repeat = 4
    sleep_sec = 1
    check_i = 0

    while not check and check_i < count_repeat:
        try:
            client = MongoClient(connect_string_to, serverSelectionTimeoutMS=60)
            client.server_info()
            check = True
        except Exception as ex:
            print(f"try {check_i}, connecting - error, sleep - {sleep_sec} sec.")
            time.sleep(sleep_sec)
            check_i += 1
    if check:
        mongoclient = client
        return mongoclient


def not_empty(field: Field):
    return Condition(field, Operations.NotEqual, '')

def valid_ip(address):
    """
    Checks if string is a valid ip-address

    :param str address:
    :rtype: bool
    """
    try:
        ipaddress.ip_address(address)
        return True
    except:
        return False

def return_massive_about_ips(ips, server, user, password):

    def prepare_row(line):
        _name = return_namecoin(line['clean_name'])
        if _name:
            _result = dict()
            _result['date_time'] = line['clean_datetime_block']
            _result['domain'] = _name['domain']
            _result['namecoin_domain'] = line['clean_name']
            _result['height'] = line['height_block']
            _result['hash_block'] = line['blockhash']
            _result['txid'] = line['txid']
            try:
                _result['operation'] = line['clean_op']
            except:
                pass
            if 'ips' in line:
                for ip in line['ips']:
                    _result_row = _result.copy()
                    _result_row['ip'] = ip.strip()
                    yield _result_row

    def return_info(search_dict, need_fields):
        rows = db[collection_name_tx].find(search_dict, need_fields)
        massive_all = [row for row in rows]

        _need_block_fields = {'_id': 1, 'height': 1}
        hashs_block = list(set([row['blockhash'] for row in massive_all]))
        _search_filter = {"_id": {"$in": hashs_block}}
        _tmp = db[collection_name_blocks].find(_search_filter, _need_block_fields)
        _cache = {}
        for row in _tmp:
            if row['_id'] not in _cache:
                _cache[row['_id']] = row['height']

        for row in massive_all:
            if row['blockhash'] in _cache:
                row['height_block'] = _cache[row['blockhash']]
            rows_for_table_lampyre = prepare_row(row)
            for _row in rows_for_table_lampyre:
                yield _row

    ip, port = server.split(":")
    dbname = "NamecoinExplorer"
    collection_name_blocks = "Blocks"
    collection_name_tx = "Tx"
    cl_mongo = init_connect_to_mongodb(ip, port, dbname, user, password)
    ips_checked = list(filter(valid_ip, ips))
    if cl_mongo:
        db = cl_mongo[dbname]
        search_dict = {"ips": {"$in": ips_checked}}
        need_fields = {'clean_name': 1,
                       'ips': 1,
                       'clean_op': 1,
                        'clean_datetime_block': 1,
                       'blockhash': 1,
                       'txid': 1,
                       '_id': 0}
        for line in return_info(search_dict, need_fields):
            yield line





def return_namecoin(namedomain):
    if namedomain.endswith(".bit"):
        return {'domain':namedomain,
                'namecoin_domain': f"d/{namedomain[:-4]}"}
    elif namedomain.startswith('d/'):
        return {'domain':namedomain[2:]+'.bit',
                'namecoin_domain':namedomain}


class NamecoinDomainExplorer(metaclass=Header):
    display_name = 'Namecoin Explorer'
    date_time = Field('Date and time Block', ValueType.Datetime)
    domain = Field('Domain', ValueType.String)
    namecoin_domain = Field('Namecoin name', ValueType.String)
    ip = Field('ip', ValueType.String)
    Netblock = Field('Netblock', ValueType.String)
    expired = Field('Status', ValueType.Boolean)
    operation = Field('operation', ValueType.String)
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


class NamecoinHistoryIPDomainMongoDB(Task):

    def __init__(self):
        super().__init__()
        self.info, self.error, self.result, self.api, self.api_key = [None] * 5

    def get_id(self):
        return '494b11ca-2a3c-4a17-91d1-b22f0569958f'

    def get_display_name(self):
        return 'Explore Namecoin IP(MongoDB)'

    def get_category(self):
        return "Blockchain:\nNamecoin"

    def get_description(self):
        return 'Return history Namecoin IP\n\nEnter parameters "8.8.8.8'

    def get_weight_function(self):
        return 'ips'

    def get_headers(self):
        return HeaderCollection(NamecoinDomainExplorer)


    def get_schemas(self):
        return SchemaCollection(NamecoinDomainIP)

    def get_graph_macros(self):
        return MacroCollection(
            Macro(name='Namecoin Schema:IP --> Domain', mapping_flags=[GraphMappingFlags.Completely],
                  schemas=[NamecoinDomainIP]))



    def get_enter_params(self):
        ep_coll = EnterParamCollection()
        ep_coll.add_enter_param('ips', 'IP', ValueType.String, is_array=True, required=True,
                                value_sources=[Attributes.System.IPAddress, Attributes.System.IPAndPort],
                                description='IPv4 addresses or IPv4 addresses, e.g.:\n192.168.1.1')
        ep_coll.add_enter_param('server', 'Host with MongoDB', ValueType.String, is_array=False, required=True,
                                default_value="68.183.0.119:27017")
        ep_coll.add_enter_param('usermongodb', 'user', ValueType.String, is_array=False, required=True,
                                default_value="anonymous")
        ep_coll.add_enter_param('passwordmongodb', 'password', ValueType.String, is_array=False, required=True,
                                default_value="anonymous")
        return ep_coll

    def execute(self, enter_params, result_writer, log_writer, temp_dir=None):
        server = enter_params.server
        ips = enter_params.ips
        user = enter_params.usermongodb
        password = enter_params.passwordmongodb

        log_writer.info("input ip-addresses:{}".format(len(ips)))
        result_lines = return_massive_about_ips(ips, server, user, password)
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
        # ips = ['185.82.218.112']
        # ips = ['132.148.40.220', '185.126.202.186', '37.44.213.187', '50.248.53.221']
        ips = ['144.76.12.6']
        # ips = ['37.44.213.187']
        server = "68.183.0.119:27017"
        usermongodb = "anonymous"
        passwordmongodb = "anonymous"


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

    NamecoinHistoryIPDomainMongoDB().execute(EnterParamsFake, WriterFake, WriterFake, None)