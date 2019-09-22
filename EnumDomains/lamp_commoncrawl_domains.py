# -*- coding: utf8 -*-
__author__ = 'sai'

try:
    from ontology import (
        Task, Header, HeaderCollection, Utils, Field, ValueType, SchemaLink, SchemaObject, Condition, Operations, Macro,
        MacroCollection, Schema, EnterParamCollection, SchemaCollection, GraphMappingFlags, BinaryType, Constants,
        Attributes, IP, Domain, DomainToDomain, Link)

except ImportError as ontology_exception:
    print('missing or invalid ontology')
    raise ontology_exception

import itertools
import requests
from urllib.parse import urlparse
import json
import concurrent.futures
from random import choice
from time import sleep
import datetime
from sys import exit

def grouper(count, iterable, fillvalue=None):
    """
    :param count: length of subblock
    :param iterable: array of data
    :param fillvalue: is fill value in last chain
    :return:
    grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    """
    args = [iter(iterable)] * count
    result = []
    for element in itertools.zip_longest(fillvalue=fillvalue, *args):
        tmp = filter(lambda y: y is not None, element)
        result.append(list(tmp))
    return result


def get_main_indexs(lgw):
    """
    simple return json from index.commoncrawl.org with set of data
    :return:
    """
    main_url_json = "https://index.commoncrawl.org/collinfo.json"
    try:
        req = requests.get(main_url_json)
        status = req.status_code
    except Exception as ex:
        lgw.error(f'something went wrong...:{str(ex)}')
    else:
        if status == 200:
            try:
                indexs = [el['cdx-api'] for el in req.json()]
                return indexs
            except Exception as ex:
                lgw.error(f'something went wrong...:{str(ex)}')


def create_commoncrawl_urls(commoncrawl_indexs, domains):
    """
    only prepare struct
    :param commoncrawl_indexs: result of Method get_main_indexs
    :param domains: what are we going to look for subdomains
    :return: list of dicts wiht urls
    """
    page_size = str(2000)
    need_urls = []
    if commoncrawl_indexs:
        template = "{}?url={}&fl=url&matchType=domain&pageSize={}&output=json"
        for crawl_index in commoncrawl_indexs:
            for domain in domains:
                _url = template.format(crawl_index, domain, page_size)
                need_urls.append({'search_domain': domain,
                                  'crawl_url': _url,
                                  'crawl_index': crawl_index})
    return need_urls


def return_info_from_block_url(block_dict_domains, log_writer):

    def extract_date_from_url(url):
        # ex.: url = 'https://index.commoncrawl.org/CC-MAIN-2018-39-index' --> 2018-09-01
        try:
            _path = urlparse(url).path
            # ex.: _path = CC-MAIN-2018-39-index
            if '/CC-MAIN-' in _path:
                _d = _path.strip('/')
                _d = _d.lstrip('CC-MAIN-').rstrip('-index')

                if '-' in _d:
                    if len(_d.split('-')) == 2:
                        _y, _w = [_d.split('-')[0], _d.split('-')[1]]
                        if len(_w) == 2:
                            m = int(_w) // 4
                            if m >= 13:
                                m = 12
                            w = int(_w) % 4
                            w = int(_w) % 4
                            y = int(_y)
                            return datetime.datetime(y, m, 1) + datetime.timedelta(weeks=w)
                        elif len(_w) == 4:
                            y = int(_w)
                            m = 1
                            d = 1
                            return datetime.datetime(y, m, d)
                else:
                    return datetime.datetime(int(_d), 1, 1)
        except Exception as e:
            print(str(e))

    def return_info_from_one_record(dict_domain_url, sess):
        get_url = dict_domain_url['crawl_url']

        search_domain = dict_domain_url['search_domain']
        status = False
        count_check = 1
        count_block = 6
        while not status and count_check < count_block:
            try:
                if count_check == 1:
                    log_writer.info(f'fetch data:{get_url}')
                else:
                    log_writer.info(f'need to repeat the request, attempt No.:{count_check}\t:{get_url}')
                response = sess.get(get_url)
                if response.ok:
                    status = True
                    text_data = response.text
            except Exception as exc:
                log_writer.info(str(exc))
            if status:
                try:
                    payload = text_data.split('\n')
                    _lines_results = [el for el in payload if '{' in el and '}' in el]
                    lines_results = [json.loads(el) for el in _lines_results]
                    _all_info = [el['url'] for el in lines_results]
                    _need_domains = [urlparse(line).netloc for line in _all_info if urlparse(line).netloc != search_domain]
                    need_domains = []
                    for domain in _need_domains:
                        if ':' in domain:
                            need_domains.append(domain.split(':')[0])
                        else:
                            need_domains.append(domain)

                    return {'search_domain': search_domain,
                            'crawl_index': dict_domain_url['crawl_index'],
                            'domains': set(need_domains),
                            'url_crawl_index': get_url,
                           'DateTimeField': extract_date_from_url(dict_domain_url['crawl_index'])}

                except:
                    log_writer.info("errors with encode lines: url - {}, domain - {}".format(get_url, search_domain))
                    status = False

            else:
                try:
                    s = response.status_code
                    log_writer.info(f'STATUS:{s}:{get_url}')
                    if s == 404:
                        return None
                except:
                    log_writer.info(f'errors:{get_url}')
            count_check += 1
            sleep(0.5)



    # on occasion list of part of header - for examples
    user_agents = ['Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13E238 Safari/601.1',
                   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/602.3.12 (KHTML, like Gecko) Version/10.0.2 Safari/602.3.12',
                   'Mozilla/5.0 (iPhone; CPU iPhone OS 9_2_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13D15 Safari/601.1',
                   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/534.59.10 (KHTML, like Gecko) Version/5.1.9 Safari/534.59.10',
                   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.78.2 (KHTML, like Gecko) Version/6.1.6 Safari/537.78.2',
                   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/601.4.4 (KHTML, like Gecko) Version/9.0.3 Safari/601.4.4',
                   'Mozilla/5.0 (iPhone; CPU iPhone OS 10_1_1 like Mac OS X) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0 Mobile/14B100 Safari/602.1',
                   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Safari/605.1.15',
                   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/601.5.17 (KHTML, like Gecko) Version/9.1 Safari/601.5.17',
                   'Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_1 like Mac OS X) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0 Mobile/15C153 Safari/604.1',
                   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/601.7.8 (KHTML, like Gecko) Version/9.1.3 Safari/601.7.8',
                   'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_2 like Mac OS X) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.0 Mobile/14F89 Safari/602.1',
                   'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_2 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/14A456 Safari/602.1',
                   'Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_6 like Mac OS X) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0 Mobile/15D100 Safari/604.1',
                   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Safari/602.1.50']

    selected_user_agents = choice(user_agents)

    headers = {'user-agent': selected_user_agents}


    session_request = requests.Session()
    session_request.headers.update(headers)
    # set 'magic' number :) random mil.sec. sleep

    union_result = []
    for one_record in block_dict_domains:
        # region pause - "magic method"
        times_for_sleep = choice([i * 0.5 for i in range(1, 10)] * 4)
        sleep(times_for_sleep)
        # pause
        # endregion
        raw_row = return_info_from_one_record(one_record, session_request)
        if raw_row:
            union_result.append(raw_row)
    return union_result


def prepare_table(rawtable):
    """
    prepare table for record
    :param rawtable: input as result from Method return_info_from_one_url
    :return: struct for result_writer(lampyre API)
    """
    fields_table = TableSubDomains.get_fields()
    table_prepared = []
    if rawtable:
        if 'domains' in rawtable:
            for row in rawtable['domains']:
                tmp = TableSubDomains.create_empty()
                for field in fields_table:
                    if field in rawtable:
                        tmp[fields_table[field]] = rawtable[field]
                tmp[fields_table['subdomain']] = row
                table_prepared.append(tmp)
    return table_prepared


def thread_async_by_page(requests_domains, threads, lgw):
    """
    async http(s) requests - async calling return_info_from_one_url
    :param requests_domains:
    :param threads:
    :param lgw:
    :return:[] list
    """
    blocks_domains = grouper(4, requests_domains)
    c_r = len(requests_domains)
    result_table = []
    lgw.info(f'number of required requests:{c_r}')
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        future_rows = {executor.submit(return_info_from_block_url, block_urls, lgw):
                           block_urls for block_urls in blocks_domains}
        i = 1
        for future in concurrent.futures.as_completed(future_rows):
            result = future.result()
            if result:
                for line in result:
                    prepared_lines = prepare_table(line)
                    for row in prepared_lines:
                        result_table.append(row)
    return result_table


def not_empty(field: Field):
    return Condition(field, Operations.NotEqual, '')


class DomainToDomainWithDate(metaclass=Link):
    name = Utils.make_link_name(Domain, Domain) + ' timeline'
    DateTime = Attributes.System.Datetime
    Begin = Domain
    End = Domain


class TableSubDomains(metaclass=Header):
    """
    table 1 for Lampyre
    """
    display_name = 'Domains(subdomains)'
    DateTimeField = Field('Date', ValueType.Datetime)
    search_domain = Field("Search domain", ValueType.String)
    subdomain = Field("Subdomain", ValueType.String)
    crawl_index = Field('CommonCrawl index', ValueType.String)
    url_crawl_index = Field('URL (CommonCrawl index)', ValueType.String)


class TableUniqueSubDomains(metaclass=Header):
    """
    table 2 for Lampyre
    """
    display_name = 'Unique Domains(subdomains)'
    search_domain = Field("Search domain", ValueType.String)
    subdomain = Field("Subdomain", ValueType.String)


class DomainToSubDomainDate(metaclass=Schema):
    name = 'Domains, Subdomains:timeline'
    Header = TableSubDomains

    SchemaDomain = SchemaObject(Domain, mapping={Domain.Domain: Header.search_domain})
    SchemaSubDomain = SchemaObject(Domain, mapping={Domain.Domain: Header.subdomain})

    SchemaDomainToDomain = DomainToDomainWithDate.between(
        SchemaDomain, SchemaSubDomain,
        mapping={DomainToDomainWithDate.DateTime: Header.DateTimeField},
        conditions=[not_empty(Header.search_domain), not_empty(Header.subdomain)])

class DomainToSubDomainUniq(metaclass=Schema):
    name = 'Domains, Subdomains'
    Header = TableUniqueSubDomains

    SchemaDomain = SchemaObject(Domain, mapping={Domain.Domain: Header.search_domain})
    SchemaSubDomain = SchemaObject(Domain, mapping={Domain.Domain: Header.subdomain})

    SchemaDomainToDomain = DomainToDomain.between(
        SchemaDomain, SchemaSubDomain,
        mapping={DomainToDomain.RelationType: Header.search_domain},
        conditions=[not_empty(Header.search_domain), not_empty(Header.subdomain)])

class CommonCrawlDataSetSubdomainExtracter(Task):

    def __init__(self):
        super().__init__()
        self.info, self.error, self.result, self.api, self.api_key = [None] * 5

    def get_id(self):
        return '41b89f4a-64c1-4b4f-84e3-73448e81953d'

    def get_display_name(self):
        return 'CommonCrawl data Set: subdomain extracter'

    def get_category(self):
        return "!Examples"

    def get_description(self):
        return 'Data from Common Crawl Index Server'

    def get_weight_function(self):
        return 'domains'

    def get_headers(self):
        htable = TableSubDomains
        htable.set_property(TableSubDomains.crawl_index.system_name, 'hidden', True)
        return HeaderCollection(htable, TableUniqueSubDomains)

    def get_schemas(self):
        return SchemaCollection(DomainToSubDomainDate, DomainToSubDomainUniq)

    def get_enter_params(self):
        ep_coll = EnterParamCollection()
        ep_coll.add_enter_param('domains', 'Domain', ValueType.String, is_array=True, required=True,
                                description='example.com')
        ep_coll.add_enter_param('c_threads', 'threads', ValueType.Integer, is_array=False,
                                required=True, predefined_values=[4, 8, 16, 32], default_value=32)
        return ep_coll

    def execute(self, enter_params, result_writer, log_writer, temp_dir=None):
        domains = set([domain.lower().strip() for domain in enter_params.domains])
        commoncrawl_indexs = get_main_indexs(lgw=log_writer)
        if not commoncrawl_indexs:
            log_writer.error('unable to get data from https://index.commoncrawl.org')
            exit(1)
        max_threads = enter_params.c_threads
        request_urls = create_commoncrawl_urls(commoncrawl_indexs, domains)

        results = thread_async_by_page(request_urls, threads=max_threads, lgw=log_writer)
        cache_for_table_2 = []

        fields_table_1 = TableSubDomains.get_fields()
        for line in sorted(results,  key=lambda line: line[fields_table_1['DateTimeField']]):
            result_writer.write_line(line, header_class=TableSubDomains)

        for row_table in results:
            search_domain = row_table[fields_table_1['search_domain']]
            sub_domain = row_table[fields_table_1['subdomain']]
            fields_table_2 = TableUniqueSubDomains.get_fields()
            if ''.join([search_domain, sub_domain]) not in cache_for_table_2:
                _tmp = TableUniqueSubDomains.create_empty()
                _tmp[fields_table_2['search_domain']] = search_domain
                _tmp[fields_table_2['subdomain']] = sub_domain
                result_writer.write_line(_tmp, header_class=TableUniqueSubDomains)
                cache_for_table_2.append(''.join([search_domain, sub_domain]))


# region Debugging
if __name__ == '__main__':
    DEBUG = True

    class EnterParamsFake:
        domains = ['group-ib.ru']
        c_threads = 32

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

    CommonCrawlDataSetSubdomainExtracter().execute(EnterParamsFake, WriterFake, WriterFake, None)
# endregion
