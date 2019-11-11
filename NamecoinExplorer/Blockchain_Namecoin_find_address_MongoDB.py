# -*- coding: utf8 -*-
__author__ = 'sai'

import time
from pymongo import MongoClient
import ipaddress
import re


# region Import System Ontology
try:
    from ontology import (Object, Link, Attribute,
        Task, Header, HeaderCollection, Utils, Field, ValueType, SchemaLink, SchemaObject, Condition, Operations, Macro,
        MacroCollection, Schema, EnterParamCollection, SchemaCollection, GraphMappingFlags, BinaryType, Constants,
        Attributes, IP, Domain, IPToDomain)
except ImportError as ontology_exception:
    print('...missing or invalid ontology')
    raise ontology_exception
# endregion


# region load Namecoin Ontology
try:
    from NamecoinOntology import (NamecoinTXnExplorer_in, NamecoinTXid, NamecoinTXidToNamecoinTXid,
                                  NamecoinTXnExplorer_out, NamecoinAddress, NamecoinTXidToAddress,
                                  NamecoinAddressToIP, NamecoinAddressToDomain)
except ImportError as ontology_exception:
    print('...missing or invalid ontology')
    raise ontology_exception
# endregion


def return_ip(text):
    result = []
    ipPattern = r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})'
    ipaddress_subtmp = re.findall(ipPattern, text)
    if ipaddress_subtmp:
        for ip in ipaddress_subtmp:
            try:
                _ip = ipaddress.ip_address(ip.strip())
                if str(_ip) not in result:
                    result.append(str(_ip))
            except:
                pass
    if len(result) > 0:
        return result


def init_connect_to_mongodb(ip, port, dbname, username=None, password=None):
    """
    :param ip:  ip server MongoDB
    :param port: 27017
    :return: True, if connected, and set value mongoclient - MongoClient
    """
    if username and password:
        connect_string_to = f'mongodb://{username}:{password}@{ip}:{port}/{dbname}'
    else:
        connect_string_to = f'mongodb://{ip}:{port}/{dbname}'

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
            print(f"try {check_i}, error:'{str(ex)}' connecting - error, sleep - 1 sec.")
            time.sleep(sleep_sec)
            check_i += 1
        else:
            return client


def not_empty(field: Field):
    return Condition(field, Operations.NotEqual, '')


def return_massive_about_addresses(addresses, server, user, password):

    def prepare_row_table_txids(line):

        _name = line.copy()
        _result = dict()

        _result['date_time'] = line['clean_datetime_block']
        _result['txid'] = line['txid']
        _result['short_txid'] = line['txid'][:8]
        _result['hash_block'] = line['blockhash']
        if 'vin' in line:
            if isinstance(line['vin'], list):
                for tx in line['vin']:
                    if 'txid' in tx:
                        for_yield_line = _result.copy()
                        for_yield_line['txid_in'] = tx['txid']
                        for_yield_line['short_txid_in'] = tx['txid'][:8]
                        yield {'value':for_yield_line,
                               'type': 'txids'}

    def prepare_row_table_address(line):

        _name = line.copy()
        _result = dict()

        _result['date_time'] = line['clean_datetime_block']
        _result['txid'] = line['txid']
        _result['short_txid'] = line['txid'][:8]
        _result['hash_block'] = line['blockhash']
        _result_massive = []
        if 'vout' in line:
            if isinstance(line['vout'], list):
                # go for vout
                for el in line['vout']:
                    for_yield_line = _result.copy()
                    if 'value' in el:
                        for_yield_line['value'] = el['value']
                    if 'scriptPubKey' in el:
                        if 'addresses' in el['scriptPubKey']:
                            if isinstance(el['scriptPubKey']['addresses'], list):
                                for_yield_line['address']= el['scriptPubKey']['addresses'][0]
                                for_yield_line['short_address'] = el['scriptPubKey']['addresses'][0][:8]
                        if 'nameOp' in el['scriptPubKey']:
                            if 'op' in el['scriptPubKey']['nameOp']:
                                for_yield_line['nameOp'] = el['scriptPubKey']['nameOp']['op']
                            if 'name' in el['scriptPubKey']['nameOp']:
                                for_yield_line['raw_name'] = el['scriptPubKey']['nameOp']['name']
                            if 'value' in el['scriptPubKey']['nameOp']:
                                for_yield_line['value_scripts'] = el['scriptPubKey']['nameOp']['value']
                    if 'raw_name' in for_yield_line:
                        _n = return_namecoin(for_yield_line['raw_name'])
                        if _n:
                            for_yield_line['namecoin_domain'] = _n['domain']
                    _tmp_ips =None
                    if 'value_scripts' in for_yield_line:
                        _tmp_ips = return_ip(for_yield_line['value_scripts'].strip())
                    if _tmp_ips:
                        for ip in _tmp_ips:
                            _row = for_yield_line.copy()
                            _row['ip'] = ip
                            yield {'value': _row,
                                       'type': 'addresses'}
                    else:
                        yield {'value': for_yield_line,
                               'type': 'addresses'}

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
            rows_for_table_txids_lampyre = prepare_row_table_txids(row)
            rows_for_table_addresses_lampyre = prepare_row_table_address(row)
            for line in rows_for_table_txids_lampyre:
                yield line
            for line in rows_for_table_addresses_lampyre:
                yield line

    if ':' in server:
        ip, port = server.split(":")
    else:
        # try default
        ip = server
        port = '27017'

    dbname = "NamecoinExplorer"
    collection_name_blocks = "Blocks"
    collection_name_tx = "Tx"
    cl_mongo = init_connect_to_mongodb(ip, port, dbname, user, password)
    if cl_mongo:
        db = cl_mongo[dbname]

        search_dict = {'$or': []}
        for address in addresses:
            _tmp_dict = {'vout.scriptPubKey.addresses': {'$regex': f"^{address}"}}
            search_dict['$or'].append(_tmp_dict)

        need_fields = {'_id': 0,
                       'hash': 0,
                       'version': 0,
                       'size': 0,
                       'locktime': 0,
                       'clean_name': 0,
                       'clean_op': 0,
                       'vsize': 0
                       }
        for line in return_info(search_dict, need_fields):
            yield line


def return_namecoin(namedomain):
    if namedomain.count(' ') == 0:
        if namedomain.endswith(".bit"):
            return {'domain': namedomain, 'namecoin_domain': f"d/{namedomain[:-4]}"}
        elif namedomain.startswith('d/'):
            return {'domain': namedomain[2:]+'.bit', 'namecoin_domain': namedomain}


class NamecoinNamecoinTxtoNamecoinTx(metaclass=Schema):
    name = f'Namecoin schema: Namecoin transaction {Constants.RIGHTWARDS_ARROW} Namecoin transaction'
    Header = NamecoinTXnExplorer_in

    SchemaNamecoinTXid_1 = SchemaObject(NamecoinTXid, mapping={NamecoinTXid.txid: Header.txid,
                                                               NamecoinTXid.txid_short: Header.short_txid})

    SchemaNamecoinTXid_2 = SchemaObject(NamecoinTXid, mapping={NamecoinTXid.txid: Header.txid_in,
                                                               NamecoinTXid.txid_short: Header.short_txid_in})


    SchemaNamecoinTXidToNamecoinTXid = NamecoinTXidToNamecoinTXid.between(
        SchemaNamecoinTXid_2, SchemaNamecoinTXid_1,
        mapping={NamecoinTXidToNamecoinTXid.DateTime: Header.date_time})


class NamecoinNamecoinTxtoNamecoinAddress(metaclass=Schema):
    name = f'Namecoin schema: Namecoin transaction {Constants.RIGHTWARDS_ARROW} other(address, domain, ip)'
    Header = NamecoinTXnExplorer_out

    SchemaNamecoinTXid = SchemaObject(NamecoinTXid, mapping={NamecoinTXid.txid: Header.txid,
                                                               NamecoinTXid.txid_short: Header.short_txid})

    SchemaAddress = SchemaObject(NamecoinAddress, mapping={NamecoinAddress.namecoint_address: Header.address,
                                                               NamecoinAddress.namecoint_address_short: Header.short_address})



    SchemaSchemaNamecoinTXid_to_SchemaAddress = NamecoinTXidToAddress.between(
        SchemaNamecoinTXid, SchemaAddress,
        mapping={NamecoinTXidToAddress.DateTime: Header.date_time,
                 NamecoinTXidToAddress.Operation: Header.nameOp,
                 NamecoinTXidToAddress.Domain: Header.raw_name,
                 NamecoinTXidToAddress.Value: Header.value})


    SchemaDomain = SchemaObject(Domain, mapping={Domain.Domain: Header.namecoin_domain})

    SchemaIP = SchemaObject(IP, mapping={IP.IP: Header.ip})
    SchemaAddressToIP = NamecoinAddressToIP.between(SchemaAddress, SchemaIP,
                                                    mapping={NamecoinAddressToIP.DateTime: Header.date_time},
                                                    conditions=[not_empty(Header.ip)]
                                                    )

    SchemaAddressToDomain = NamecoinAddressToDomain.between(SchemaAddress, SchemaDomain,
                                                    mapping={NamecoinAddressToDomain.DateTime: Header.date_time},
                                                    conditions=[not_empty(Header.namecoin_domain)]
                                                            )

    SchemaIPToDomain = IPToDomain.between(
        SchemaIP, SchemaDomain,
        mapping={IPToDomain.Resolved: Header.date_time},
        conditions=[not_empty(Header.namecoin_domain), not_empty(Header.ip)])


class NamecoinHistoryAddressesMongoDB(Task):

    def __init__(self):
        super().__init__()
        self.info, self.error, self.result, self.api, self.api_key = [None] * 5

    def get_id(self):
        return '930c1bdd-2613-498e-bf2a-5868b03b99b2'

    def get_display_name(self):
        return 'Explore Namecoin Addresses(MongoDB)'

    def get_category(self):
        return "Blockchain:\nNamecoin"

    def get_description(self):
        return 'Return history operations\n\nEnter parameters "Addresses"'

    def get_weight_function(self):
        return 'txids'

    def get_headers(self):
        return HeaderCollection(NamecoinTXnExplorer_in, NamecoinTXnExplorer_out)

    def get_graph_macros(self):
        return MacroCollection(
            Macro(name=f'Namecoin schema: Namecoin transaction {Constants.RIGHTWARDS_ARROW} Namecoin transaction',
                  mapping_flags=[GraphMappingFlags.Completely],
                  schemas=[NamecoinNamecoinTxtoNamecoinTx]),
            Macro(name=f'Namecoin schema: Namecoin transaction {Constants.RIGHTWARDS_ARROW} other(address, domain, ip)',
                 mapping_flags=[GraphMappingFlags.Completely], schemas=[NamecoinNamecoinTxtoNamecoinAddress])
        )

    def get_schemas(self):
        return SchemaCollection(NamecoinNamecoinTxtoNamecoinTx, NamecoinNamecoinTxtoNamecoinAddress)

    def get_enter_params(self):
        ep_coll = EnterParamCollection()
        ep_coll.add_enter_param('addresses', 'Namecoin addresses', ValueType.String, is_array=True, required=True,
                                value_sources=[NamecoinAddress.namecoint_address,
                                               NamecoinAddress.namecoint_address_short],
                                description='Namecoin Address, e.g.:\nMzHtiNhzd - (min. 8 symbols)')
        ep_coll.add_enter_param('server', 'Host with MongoDB', ValueType.String, is_array=False, required=True,
                                default_value="68.183.0.119:27017")
        ep_coll.add_enter_param('usermongodb', 'user', ValueType.String, is_array=False, required=True,
                                default_value="anonymous")
        ep_coll.add_enter_param('passwordmongodb', 'password', ValueType.String, is_array=False, required=True,
                                default_value="anonymous")
        return ep_coll

    def execute(self, enter_params, result_writer, log_writer, temp_dir=None):
        server = enter_params.server
        user = enter_params.usermongodb
        password = enter_params.passwordmongodb

        addresses = set([a.strip() for a in enter_params.addresses])

        log_writer.info("Number of txids:{}".format(len(addresses)))
        result_lines = return_massive_about_addresses(addresses, server, user, password)

        table_txids = []
        table_addresses = []

        for row in result_lines:
            if row['type'] == 'txids':
                table_txids.append(row['value'])
            elif row['type'] == 'addresses':
                table_addresses.append(row['value'])

        for line in sorted(table_txids,  key=lambda line: line['date_time']):
            fields_table = NamecoinTXnExplorer_in.get_fields()
            tmp = NamecoinTXnExplorer_in.create_empty()
            for field in fields_table:
                if field in line:
                    tmp[fields_table[field]] = line[field]
            result_writer.write_line(tmp, header_class=NamecoinTXnExplorer_in)

        for line in sorted(table_addresses,  key=lambda line: line['date_time']):
            fields_table = NamecoinTXnExplorer_out.get_fields()
            tmp = NamecoinTXnExplorer_out.create_empty()
            for field in fields_table:
                if field in line:
                    tmp[fields_table[field]] = line[field]
            result_writer.write_line(tmp, header_class=NamecoinTXnExplorer_out)


if __name__ == '__main__':
    DEBUG = True

    class EnterParamsFake:
        addresses = ['MzHtiNhzd']
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

    NamecoinHistoryAddressesMongoDB().execute(EnterParamsFake, WriterFake, WriterFake, None)