# -*- coding: utf8 -*-
__author__ = 'sai'

try:
    from ontology import (
        Task, Header, HeaderCollection, Utils, Field, ValueType, SchemaLink, SchemaObject, Condition, Operations, Macro,
        MacroCollection, Schema, EnterParamCollection, SchemaCollection, GraphMappingFlags, BinaryType, Constants,
        Attributes, IP, Port)

except ImportError as ontology_exception:
    print('missing or invalid ontology')
    raise ontology_exception

import requests
from urllib.parse import urlparse
import json
import concurrent.futures
from random import choice
from time import sleep


def get_main_indexs():
    """
    simple return json from index.commoncrawl.org with set of data
    :return:
    """
    main_url_json = "https://index.commoncrawl.org/collinfo.json"
    try:
        req = requests.get(main_url_json)
        status = req.status_code
    except:
        status = False
    if not(status and status == 200):
        return False
    else:
        try:
            indexs = [el['cdx-api'] for el in req.json()]
            return indexs
        except:
            return False


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


def return_info_from_one_url(dict_domain_url, lgw):
    """

    :param dict_domain_url: dict as 1 element from list, from result of Method create_commoncrawl_urls
    :param lgw: log writer from lampyre api, for printing to "terminal"
    :return: struct - dict, see below
    """
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

    get_url = dict_domain_url['crawl_url']
    search_domain = dict_domain_url['search_domain']

    # set 'magic' number :) random mil.sec. sleep
    times_for_sleep = choice([i * 0.5 for i in range(1, 10)] * 4)
    sleep(times_for_sleep)

    try:
        req = requests.get(get_url, headers=headers, timeout=(2, 5))
        status = req.status_code
    except Exception as e:
        status = False
        status_exception = str(e)
    if status:
        if status == 200:
            try:
                payload = req.text.split('\n')
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
                        'url_crawl_index': get_url}
            except:
                lgw.info("errors with encode lines: url - {}, domain - {}".format(get_url, search_domain))
                return False
        else:
            lgw.info("errors: {}, url:{}".format(status, get_url))
            return False

    else:
        lgw.info("errors, exception:{}".format(status_exception))
        return False


class TableSubDomains(metaclass=Header):
    """
    table for Lampyre
    """
    display_name = 'Subdomains'
    search_domain = Field("Search domain", ValueType.String)
    subdomain = Field("Subdomain", ValueType.String)
    crawl_index = Field('CommonCrawl index', ValueType.String)
    url_crawl_index = Field('URL (CommonCrawl index)', ValueType.String)


def prepare_table(rawtable):
    """
    prepare table for record
    :param rawtable: input as result from Method return_info_from_one_url
    :return: struct for result_writer(lampyre API)
    """
    fields_table = TableSubDomains.get_fields()
    table_prepared = []
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
    :return:yield record for result_writer(lampyre API)
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        future_rows = {executor.submit(return_info_from_one_url, dict_domain_url, lgw):
                           dict_domain_url for dict_domain_url in requests_domains}
        i = 1
        for future in concurrent.futures.as_completed(future_rows):
            _dict_domain_url = future_rows[future]
            crw_index = _dict_domain_url['crawl_index']
            result = future.result()
            if result:
                lgw.info("{}:{}".format(i, crw_index))
                for line in prepare_table(result):
                    yield line
                i += 1


class CommonCrawlDataSetSubdomainExtracter(Task):

    def __init__(self):
        super().__init__()
        self.info, self.error, self.result, self.api, self.api_key = [None] * 5

    def get_id(self):
        return '41b89f4a-64c1-4b4f-84e3-73448e81953d'

    def get_display_name(self):
        return 'CommonCrawl data set subdomain extracter'

    def get_category(self):
        return "!Examples"

    def get_description(self):
        return 'Data from Common Crawl Index Server'

    def get_weight_function(self):
        return 'domains'

    def get_headers(self):
        return HeaderCollection(TableSubDomains)

    def get_enter_params(self):
        ep_coll = EnterParamCollection()
        ep_coll.add_enter_param('domains', 'Domain', ValueType.String, is_array=True, required=True,
                                description='example.com')
        ep_coll.add_enter_param('c_threads', 'threads', ValueType.Integer, is_array=False,
                                required=True, predefined_values=[4, 8, 16], default_value=8)
        return ep_coll

    def execute(self, enter_params, result_writer, log_writer, temp_dir=None):
        domains = set([domain.lower() for domain in enter_params.domains])
        commoncrawl_indexs = get_main_indexs()
        max_threads = enter_params.c_threads
        request_urls = create_commoncrawl_urls(commoncrawl_indexs, domains)
        results = thread_async_by_page(request_urls, threads=max_threads, lgw=log_writer)
        for row_table in results:
            result_writer.write_line(row_table, header_class=TableSubDomains)


# region Debugging
if __name__ == '__main__':
    DEBUG = True

    class EnterParamsFake:
        domains = ['habr.ru']
        c_threads = 4

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
