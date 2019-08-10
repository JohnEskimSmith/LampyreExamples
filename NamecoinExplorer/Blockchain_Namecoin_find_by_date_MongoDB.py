# -*- coding: utf8 -*-
__author__ = 'sai'

import time
from pymongo import MongoClient
from datetime import timedelta, datetime


try:
    from ontology import (
        Task, Header, HeaderCollection, Utils, Field, ValueType, SchemaLink, SchemaObject, Condition, Operations, Macro,
        MacroCollection, Schema, EnterParamCollection, RelativeDate, ReferencePoint, SchemaCollection, GraphMappingFlags, BinaryType, Constants,
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
            print(f"try {check_i}, connecting - error, sleep - 1 sec.")
            time.sleep(sleep_sec)
            check_i += 1
    if check:
        mongoclient = client
        return mongoclient



def not_empty(field: Field):
    return Condition(field, Operations.NotEqual, '')


def return_massive_about_domains_between_dates(start, stop, what_about_ip, server, user, password):

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

            if what_about_ip:
                for ip in line['ips']:
                    _result['ip'] = ip
                    yield _result
            else:
                if 'ips' in line:
                    for ip in line['ips']:
                        _result['ip'] = ip
                        yield _result
                else:
                    _result['ip'] = ''
                    yield _result


    ip, port = server.split(":")
    dbname = "NamecoinExplorer"
    collection_name_blocks = "Blocks"
    collection_name_tx = "Tx"

    cl_mongo = init_connect_to_mongodb(ip, port, dbname, user, password)
    if cl_mongo:
        db = cl_mongo[dbname]

        need_fields = {'clean_name': 1,
                       'ips': 1,
                        'clean_datetime_block': 1,
                       'blockhash': 1,
                       'txid': 1,
                       '_id': 0}

        if not what_about_ip:
            search_dict ={'clean_datetime_block': {'$gte':start, '$lte': stop},
                          'clean_name': {'$exists': 1}}
        else:
            search_dict = {'clean_datetime_block': {'$gte':start, '$lte': stop},
                           'ips': {'$exists': 1},
                           'clean_name':{'$exists': 1}}

        rows = db[collection_name_tx].find(search_dict, need_fields)
        for row in rows:
            _block = {'_id':row['blockhash']}
            _need_fields_block = {'height': 1, '_id': 0}
            _tmp = db[collection_name_blocks].find_one(_block, _need_fields_block)
            row['height_block'] = _tmp['height']
            for _row in prepare_row(row):
                yield _row


def return_namecoin(namedomain):
    if namedomain.endswith(".bit"):
        return {'domain':namedomain, 'namecoin_domain': f"d/{namedomain[:-4]}"}
    elif namedomain.startswith('d/'):
        return {'domain':namedomain[2:]+'.bit', 'namecoin_domain':namedomain}


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


class NamecoinHistoryDomainIPDateMongoDB(Task):

    def __init__(self):
        super().__init__()
        self.info, self.error, self.result, self.api, self.api_key = [None] * 5

    def get_id(self):
        return '721b8ef6-b0e3-48b5-bf68-87c010fad6ff'

    def get_display_name(self):
        return 'Explore Namecoin for specific dates(MongoDB)'

    def get_category(self):
        return "Blockchain:\tNamecoin"

    def get_description(self):
        return 'Return history Namecoin names'

    # def get_weight_function(self):
    #     return 'domains'

    def get_headers(self):
        return HeaderCollection(NamecoinDomainExplorer)

    def get_schemas(self):
        return SchemaCollection(NamecoinDomainIP)

    def get_enter_params(self):

        # today = datetime.datetime.now()
        # today = "2019-01-01"

        ep_coll = EnterParamCollection()

        ep_coll.add_enter_param('start_date', 'From date', ValueType.Datetime,
                                default_value = RelativeDate(ReferencePoint.Today, timedelta(weeks=-12)))
        ep_coll.add_enter_param('stop_date', 'To date', ValueType.Datetime,
                                default_value=RelativeDate(ReferencePoint.Now, timedelta(0)))

        ep_coll.add_enter_param('check_ip', 'Only with IP-addresses', ValueType.Boolean, required=True,
                                default_value=False)

        ep_coll.add_enter_param('server', 'host with MongoDB', ValueType.String, is_array=False, required=True,
                                default_value="68.183.0.119:27017")
        ep_coll.add_enter_param('usermongodb', 'user', ValueType.String, is_array=False, required=True,
                                default_value="anonymous")
        ep_coll.add_enter_param('passwordmongodb', 'password', ValueType.String, is_array=False, required=True,
                                default_value="anonymous")

        return ep_coll

    def execute(self, enter_params, result_writer, log_writer, temp_dir=None):
        start_date = enter_params.start_date
        stop_date = enter_params.stop_date
        server = enter_params.server
        user = enter_params.usermongodb
        password = enter_params.passwordmongodb

        sd = stop_date-start_date
        boolean_ip = enter_params.check_ip
        log_writer.info("searching:{} days".format(sd.days))
        log_writer.info("from:{}, to:{}".format(start_date, stop_date))
        result_lines = return_massive_about_domains_between_dates(start_date, stop_date, boolean_ip, server, user, password)
        i = 1
        for line in result_lines:
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
        start_date = datetime.strptime('2019-08-07', '%Y-%m-%d')
        stop_date = datetime.strptime('2019-08-08', '%Y-%m-%d')
        server = "68.183.0.119:27017"
        usermongodb = "anonymous"
        passwordmongodb = "anonymous"
        check_ip = False

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

    NamecoinHistoryDomainIPDateMongoDB().execute(EnterParamsFake, WriterFake, WriterFake, None)