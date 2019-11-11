# -*- coding: utf8 -*-
__author__ = 'sai'

import time
from pymongo import MongoClient


# region Import System Ontology
try:
    from ontology import (
        Object, Task, Link, Attribute, Header, HeaderCollection, Utils, Field, ValueType, SchemaLink, SchemaObject, Condition, Operations, Macro,
        MacroCollection, Schema, EnterParamCollection, SchemaCollection, GraphMappingFlags, BinaryType, Constants,
        Attributes, IP, Domain, IPToDomain, Netblock, IPToNetblock)

except ImportError as ontology_exception:
    print('...missing or invalid ontology')
    raise ontology_exception
# endregion


# region load Namecoin Ontology
try:
    from NamecoinOntology import (NamecoinTXnExplorer_in, NamecoinTXid, NamecoinTXidToNamecoinTXid,
                                  NamecoinTXnExplorer_out, NamecoinAddress, NamecoinTXidToAddress,
                                  NamecoinAddressToIP, NamecoinAddressToDomain,
                                  NamecoinDomainExplorer, NamecoinTXidToDomain,
                                  NamecoinTXidToIP, NamecoinTXidToAddressValue, NamecoinAddressToTXidValue,
                                  UnionTxAddress)
except ImportError as ontology_exception:
    print('...missing or invalid ontology')
    raise ontology_exception
# endregion


chain_symbol_1 = '\u293e'


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


def prepare_row_txaddress(line):
    _result = dict()
    _result['date_time'] = line['clean_datetime_block']
    _result['txid'] = line['txid']
    _result['short_txid'] = line['txid'][:8]

    if 'vout' in line:
        if isinstance(line['vout'], list):
            for element in line['vout']:
                _result['value'] = element['value']
                if 'scriptPubKey' in element:
                    if 'addresses' in element['scriptPubKey']:
                        if isinstance(element['scriptPubKey']['addresses'], list):
                            for a in element['scriptPubKey']['addresses']:
                                _tmp = _result.copy()
                                _tmp['address'] = a
                                _tmp['short_address']= a[:8]
                                yield _tmp


def return_massive_simple_about_addresses_1(addresses, server, user, password):

    def return_info_simple(search_dict, need_fields):
        rows = db[collection_name_tx].find(search_dict, need_fields)
        massive_all = [row for row in rows]

        for row in massive_all:
            rows_for_table_SimpleTxAddress = prepare_row_txaddress(row)
            for line in rows_for_table_SimpleTxAddress:
                yield line

    if ':' in server:
        ip, port = server.split(":")
    else:
        # try default
        ip = server
        port = '27017'

    dbname = "NamecoinExplorer"
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
                       'size':0,
                       'locktime': 0,
                       'clean_name': 0,
                       'clean_op': 0,
                       'vsize': 0
                       }
        for line in return_info_simple(search_dict, need_fields):
            yield line


def return_massive_simple_about_txids_2(_txids, server, user, password):

    if ':' in server:
        ip, port = server.split(":")
    else:
        # try default
        ip = server
        port = '27017'

    dbname = "NamecoinExplorer"
    collection_name_tx = "Tx"
    cl_mongo = init_connect_to_mongodb(ip, port, dbname, user, password)
    if cl_mongo:
        db = cl_mongo[dbname]
        need_fields = {'_id':0,
                       'txid':1}
        search_dict = {'vin.txid':{"$in": _txids}}
        rows = db[collection_name_tx].find(search_dict, need_fields)
        txids = [row['txid'] for row in rows]

        search_dict = {'txid':{"$in": txids}}

        need_fields = {'_id': 0,
                       'vin': 1,
                       'txid': 1}
        rows = db[collection_name_tx].find(search_dict, need_fields)
        massive_all = [row for row in rows]
        sub_result = []
        for line in massive_all:
            if 'vin' in line:
                for element in line['vin']:
                    _tmp = dict()
                    _tmp['txid'] = line['txid']
                    _tmp['cross_txid'] = element['txid']
                    _tmp['vout'] = element['vout']
                    sub_result.append(_tmp)
        for row in sub_result:
            search_dict = {'txid': row['cross_txid']}
            need_fields = {'_id': 0,
                           'vout': 1,
                           'clean_datetime_block': 1}
            element = db[collection_name_tx].find_one(search_dict, need_fields)
            line = dict()
            line['date_time'] = element['clean_datetime_block']
            line['address'] = element['vout'][row['vout']]['scriptPubKey']['addresses'][0]
            line['short_address'] = line['address'][:8]
            line['value'] = element['vout'][row['vout']]['value']
            line['txid'] = row['txid']
            line['short_txid'] = row['txid'][:8]
            yield line


def check_direction_1(field: Field):
    return Condition(field, Operations.Equals, 1)


def check_direction_2(field: Field):
    return Condition(field, Operations.Equals, 2)


class SchemaNamecoinUnioanTxAddressValues(metaclass=Schema):
    name = f'Namecoin schemas: \n1. transaction {Constants.RIGHTWARDS_ARROW} address(value)\n2. address(value) {Constants.LEFTWARDS_ARROW} transaction'
    Header = UnionTxAddress

    SchemaNamecoinTXid = SchemaObject(NamecoinTXid, mapping={NamecoinTXid.txid: Header.txid,
                                                               NamecoinTXid.txid_short: Header.short_txid})

    SchemaAddress1 = SchemaObject(NamecoinAddress, mapping={NamecoinAddress.namecoint_address: Header.address,
                                                           NamecoinAddress.namecoint_address_short: Header.short_address})
    SchemaAddress2 = SchemaObject(NamecoinAddress, mapping={NamecoinAddress.namecoint_address: Header.address,
                                                           NamecoinAddress.namecoint_address_short: Header.short_address})

    SchemaLinkTxtoAddressValues = NamecoinTXidToAddressValue.between(
        SchemaNamecoinTXid, SchemaAddress1,
        mapping={NamecoinTXidToAddressValue.DateTime: Header.date_time,
                 NamecoinTXidToAddressValue.Value: Header.value},
        conditions=[check_direction_1(Header.direction)])

    SchemaLinkAddresstoTxValues = NamecoinAddressToTXidValue.between(
        SchemaAddress2, SchemaNamecoinTXid,
        mapping={NamecoinAddressToTXidValue.DateTime: Header.date_time,
                 NamecoinAddressToTXidValue.Value: Header.value},
        conditions=[check_direction_2(Header.direction)])


class NamecoinHistoryChainSearchAddressesMongoDB(Task):

    def __init__(self):
        super().__init__()
        self.info, self.error, self.result, self.api, self.api_key = [None] * 5

    def get_id(self):
        return '838bed91-36d1-47b2-9be9-4607aed59829'

    def get_display_name(self):
        return 'Chain search by address Namecoin(MongoDB)'

    def get_category(self):
        return "Blockchain:\nNamecoin"

    def get_description(self):
        return 'Return history operations'

    def get_weight_function(self):
        return 'txids'

    def get_headers(self):
        htable = UnionTxAddress
        htable.set_property(UnionTxAddress.direction.system_name, 'hidden', True)
        return HeaderCollection(UnionTxAddress)

    def get_schemas(self):
        return SchemaCollection(SchemaNamecoinUnioanTxAddressValues)

    def get_graph_macros(self):
        return MacroCollection(
            Macro(name=f'{chain_symbol_1} search by Namecoin Address', mapping_flags=[GraphMappingFlags.Completely],
                  schemas=[SchemaNamecoinUnioanTxAddressValues]))


    def get_enter_params(self):
        ep_coll = EnterParamCollection()
        ep_coll.add_enter_param('addresses', 'Namecoin addresses', ValueType.String, is_array=True, required=True,
                                value_sources=[NamecoinAddress.namecoint_address,
                                               NamecoinAddress.namecoint_address_short],
                                description='Namecoin Address, e.g.:\nMzHtiNhz - (min. 8 symbols)')
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

        _table = list(return_massive_simple_about_addresses_1(addresses, server, user, password))
        need_input_tx = list(set([row['txid'] for row in _table]))

        table = []
        union_table = []
        fields_table = UnionTxAddress.get_fields()

        for row in _table:
            row['SymbolDirection'] = Constants.RIGHTWARDS_ARROW
            row['direction'] = 1
            table.append(row)

        for line in sorted(table, key=lambda line: line['date_time']):
            tmp = UnionTxAddress.create_empty()
            for field in fields_table:
                if field in line:
                    tmp[fields_table[field]] = line[field]
            union_table.append(tmp)


        _table = return_massive_simple_about_txids_2(need_input_tx, server, user, password)
        table = []
        for row in _table:
            row['SymbolDirection'] = Constants.LEFTWARDS_ARROW
            row['direction'] = 2
            table.append(row)

        for line in sorted(table, key=lambda line: line['date_time']):
            tmp = UnionTxAddress.create_empty()
            for field in fields_table:
                if field in line:
                    tmp[fields_table[field]] = line[field]
            union_table.append(tmp)

        for tmp_row in sorted(union_table, key=lambda line: line[fields_table['date_time']]):
            result_writer.write_line(tmp_row, header_class=UnionTxAddress)



if __name__ == '__main__':
    DEBUG = True

    class EnterParamsFake:
        addresses = ["N2rgk2Ev"]

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

    NamecoinHistoryChainSearchAddressesMongoDB().execute(EnterParamsFake, WriterFake, WriterFake, None)