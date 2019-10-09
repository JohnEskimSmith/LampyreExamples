# -*- coding: utf8 -*-
__author__ = 'sai'

import time
from pymongo import MongoClient
import ipaddress
import re

try:
    from ontology import (Object, Link, Attribute,
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


def return_massive_simple_about_txids_1(txids, server, user, password):

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
        for txid in txids:
            _tmp_dict = {'txid': {'$regex': f"^{txid}"}}
            search_dict['$or'].append(_tmp_dict)

        need_fields = {'_id': 0,
                       'hash':0,
                       'version':0,
                       'size':0,
                       'locktime':0,
                       'clean_name':0,
                       'clean_op':0,
                       'vsize':0
                       }
        for line in return_info_simple(search_dict, need_fields):
            yield line


def return_massive_simple_about_txids_2(txids, server, user, password):

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
        for txid in txids:
            _tmp_dict = {'txid': {'$regex': f"^{txid}"}}
            search_dict['$or'].append(_tmp_dict)

        need_fields = {'_id': 0,
                       'vin':1,
                       'txid':1}
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
                           'clean_datetime_block':1}
            element = db[collection_name_tx].find_one(search_dict, need_fields)
            line = dict()
            line['date_time'] = element['clean_datetime_block']
            line['address'] = element['vout'][row['vout']]['scriptPubKey']['addresses'][0]
            line['short_address'] = line['address'][:8]
            line['value'] = element['vout'][row['vout']]['value']
            line['txid'] = row['txid']
            line['short_txid'] = row['txid'][:8]
            yield line


class SimpleTxAddress(metaclass=Header):
    display_name = f'Namecoin Simple: Tx{Constants.RIGHTWARDS_ARROW}Address'
    date_time = Field('Date and time Block', ValueType.Datetime)
    txid = Field('txid', ValueType.String)
    short_txid = Field('Short txid(8)', ValueType.String)
    address = Field('address', ValueType.String)
    short_address = Field('Short address(8)', ValueType.String)
    value = Field('Value(coins, NMC)', ValueType.Float)


class SimpleAddressTx(metaclass=Header):
    display_name = f'Namecoin Simple: Address{Constants.RIGHTWARDS_ARROW}Tx'
    date_time = Field('Date and time Block', ValueType.Datetime)
    address = Field('address', ValueType.String)
    short_address = Field('Short address(8)', ValueType.String)
    value = Field('Value(coins, NMC)', ValueType.Float)
    txid = Field('txid', ValueType.String)
    short_txid = Field('Short txid(8)', ValueType.String)


class NamecoinTXid(metaclass=Object):
    name = "Namecoin transaction"
    txid = Attribute("Transaction id", ValueType.String)
    txid_short = Attribute("Transaction id (short)", ValueType.String)
    IdentAttrs = [txid]
    CaptionAttrs = [txid_short]
    Image = Utils.base64string(r"C:\habr\objects\TX.png")


class NamecoinAddress(metaclass=Object):
    name = "Namecoin address"
    namecoint_address = Attribute("Namecoin address", ValueType.String)
    namecoint_address_short = Attribute("Namecoin address (short)", ValueType.String)
    IdentAttrs = [namecoint_address]
    CaptionAttrs = [namecoint_address_short]
    Image = Utils.base64string(r"C:\habr\objects\namecoin.png")


class NamecoinTXidToAddressValue(metaclass=Link):
    name = 'Transaction to Address'
    DateTime = Attributes.System.Datetime
    Value = Attribute("Coins(Value)", ValueType.Float)
    CaptionAttrs = [Value,  DateTime]
    Begin = NamecoinTXid
    End = NamecoinAddress


class NamecoinAddressToTXidValue(metaclass=Link):
    name = 'Address to Transaction'
    DateTime = Attributes.System.Datetime
    Value = Attribute("Coins(Value)", ValueType.Float)
    CaptionAttrs = [Value,  DateTime]
    Begin = NamecoinAddress
    End = NamecoinTXid


class SchemaNamecoinTxtoAddressValues(metaclass=Schema):
    name = f'Namecoin schema: transaction {Constants.RIGHTWARDS_ARROW} address(value)'
    Header = SimpleTxAddress

    SchemaNamecoinTXid = SchemaObject(NamecoinTXid, mapping={NamecoinTXid.txid: Header.txid,
                                                               NamecoinTXid.txid_short: Header.short_txid})

    SchemaAddress = SchemaObject(NamecoinAddress, mapping={NamecoinAddress.namecoint_address: Header.address,
                                                           NamecoinAddress.namecoint_address_short: Header.short_address})

    SchemaLinkTxtoAddressValues = NamecoinTXidToAddressValue.between(
        SchemaNamecoinTXid, SchemaAddress,
        mapping={NamecoinTXidToAddressValue.DateTime: Header.date_time,
                 NamecoinTXidToAddressValue.Value: Header.value})


class SchemaNamecoinAddresstoTxValues(metaclass=Schema):
    name = f'Namecoin schema: address(value) {Constants.RIGHTWARDS_ARROW} transaction'
    Header = SimpleAddressTx

    SchemaNamecoinTXid = SchemaObject(NamecoinTXid, mapping={NamecoinTXid.txid: Header.txid,
                                                               NamecoinTXid.txid_short: Header.short_txid})

    SchemaAddress = SchemaObject(NamecoinAddress, mapping={NamecoinAddress.namecoint_address: Header.address,
                                                           NamecoinAddress.namecoint_address_short: Header.short_address})

    SchemaLinkAddresstoTxValues = NamecoinAddressToTXidValue.between(
        SchemaAddress, SchemaNamecoinTXid,
        mapping={NamecoinAddressToTXidValue.DateTime: Header.date_time,
                 NamecoinAddressToTXidValue.Value: Header.value})

class NamecoinHistorySimpleAddressesTXMongoDB(Task):

    def __init__(self):
        super().__init__()
        self.info, self.error, self.result, self.api, self.api_key = [None] * 5

    def get_id(self):
        return '75e40a42-3975-4967-aeba-d8f5c9a22352'

    def get_display_name(self):
        return 'Simple search by address or transaction Namecoin(MongoDB)'

    def get_category(self):
        return "Blockchain:\nNamecoin"

    def get_description(self):
        return 'Return history operations'

    def get_weight_function(self):
        return 'txids'

    def get_headers(self):
        return HeaderCollection(SimpleTxAddress, SimpleAddressTx)

    def get_schemas(self):
        return SchemaCollection(SchemaNamecoinTxtoAddressValues, SchemaNamecoinAddresstoTxValues)

    def get_enter_params(self):
        ep_coll = EnterParamCollection()
        ep_coll.add_enter_param('identificators', 'Namecoin identificators', ValueType.String, is_array=True, required=True,
                              description='Namecoin identificators, e.g.:\naddresses\nid transaction')
        ep_coll.add_enter_param('type_ident', 'Type of Namecoin ident.', ValueType.String, is_array=False,
                                required=True, predefined_values=['transaction', 'address'],
                                default_value='transaction',
                                description='Type of Namecoin identificator')
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

        idents = set([a.strip() for a in enter_params.identificators])
        type_ident = enter_params.type_ident
        if type_ident == 'transaction':
            table_1 = return_massive_simple_about_txids_1(idents, server, user, password)
            for line in sorted(table_1, key=lambda line: line['date_time']):
                fields_table = SimpleTxAddress.get_fields()
                tmp = SimpleTxAddress.create_empty()
                for field in fields_table:
                    if field in line:
                        tmp[fields_table[field]] = line[field]
                result_writer.write_line(tmp, header_class=SimpleTxAddress)
            table_2  = return_massive_simple_about_txids_2(idents, server, user, password)
            for line in sorted(table_2, key=lambda line: line['date_time']):
                fields_table = SimpleAddressTx.get_fields()
                tmp = SimpleAddressTx.create_empty()
                for field in fields_table:
                    if field in line:
                        tmp[fields_table[field]] = line[field]
                result_writer.write_line(tmp, header_class=SimpleAddressTx)




if __name__ == '__main__':
    DEBUG = True

    class EnterParamsFake:
        identificators = ["cd768b433d4bb94d19fa6adb6b3e56936a356a7d943282c4fdd9495018296f81"]
        type_ident = "transaction"
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

    NamecoinHistorySimpleAddressesTXMongoDB().execute(EnterParamsFake, WriterFake, WriterFake, None)