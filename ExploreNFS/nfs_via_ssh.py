# -*- coding: utf8 -*-

import datetime
import ipaddress
import concurrent.futures
import time
import collections
import string

try:
    from ontology import (Task, Header, Field, ValueType, EnterParamCollection, Attributes)
except ImportError as ontology_error:
    print('ontology not found')
    raise ontology_error

def reparse_ip_hosts(hosts):
    result = []
    _hosts = []
    if not isinstance(hosts, collections.abc.Iterable):
        _hosts = [hosts]
    elif isinstance(hosts, str):
        _hosts = [hosts]
    elif hasattr(hosts, 'copy'):
        _hosts = hosts.copy()
    for host in _hosts:
        _tmp = None
        if '/' in host:
            try:
                _tmp = list(map(str, ipaddress.ip_network(host)))
            except ValueError:
                pass
        else:
            try:
                _tmp = [str(ipaddress.ip_address(host))]
            except ValueError:
                pass
        if _tmp:
            result.extend(_tmp)
    return result


def reparse_record_from_exports(record_host):
    add_block = {}
    _tmp = None
    if '/' in record_host:
        try:
            _tmp = str(ipaddress.ip_network(record_host))
            add_block['network'] = _tmp
            _tmp = list(map(str, ipaddress.ip_network(record_host)))
            if len(_tmp) == 1:  # if record_host == '192.168.1.1/32' and _tmp = ['192.168.1.1']
                add_block['ip'] = record_host.split('/')[0]
        except:
            try:
                _tmp = str(ipaddress.ip_address(record_host.split('/')[0]))
                add_block['ip'] = _tmp
            except:
                pass
    else:
        try:
            _tmp = str(ipaddress.ip_address(record_host))
            add_block['ip'] = _tmp
        except:
            pass
        if not _tmp:
            if 'everyone' not in record_host and record_host != '*' and record_host != 'unknown':
                if all(c in string.printable for c in record_host):
                    add_block['host'] = record_host
    add_block['status'] = record_host
    return add_block


def return_info_nfs(client, ip, timeouts=10):
    print(f'working on: {ip}')
    return_result = []
    remote_command = f"timeout {timeouts} showmount --no-headers -e {ip}"
    result = None
    try:
        stdin, stdout, stderr = client.exec_command(remote_command, timeout=timeouts)
        result = stdout.read()
    except:
        pass
    if result:
        try:
            output = result.decode('utf-8')
            if output.count('\n') >= 1:
                for row in [line for line in output.split('\n') if line != '']:
                    if ' ' in row:
                        _tmp = None
                        info = list(filter(lambda z: len(z) > 0, row.split(' ')))
                        d = datetime.datetime.now().replace(microsecond=0)
                        if len(info) == 1:
                            _tmp = {'host_query': ip, 'shared_path': info[0], 'status_ip': 'unknown', 'current_day': d}
                        elif len(info) > 1:
                            if ',' in info[1]:
                                for _ip in info[1].split(','):
                                    _tmp = {'host_query': ip, 'shared_path': info[0], 'status_ip': _ip,
                                            'current_day': d}
                                    return_result.append(_tmp)
                            else:
                                _tmp = {'host_query': ip, 'shared_path': info[0], 'status_ip': info[1],
                                        'current_day': d}
                        return_result.append(_tmp)
        except:
            pass
    return return_result


def thread_async_nfs_one_client(hosts_ports, threads=4, req_timeout=10):
    import paramiko
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy)
    client.connect(SSH_HOST, banner_timeout=30, auth_timeout=30, port=SSH_PORT, username=USERNAME,
                   password=PASSWORD)
    time.sleep(1.5)
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        future_rows = {executor.submit(return_info_nfs, client, ip, req_timeout): ip for ip, port in hosts_ports}
        for future in concurrent.futures.as_completed(future_rows):
            _ip = future_rows[future]
            try:
                result = future.result()
                if result:
                    for row in result:
                        if row:
                            yield row
            except:
                pass


def reparse_result_rows(rows):
    _cache = []
    _tmp_rows = []
    keys_for_distinct = ['host_query', 'shared_path', 'status_ip']
    for row in filter(lambda z: z, rows):
        _cache_elem = get_uniq_row(row, keys_for_distinct)
        if _cache_elem not in _cache:
            _tmp_rows.append(row)
            _cache.append(_cache_elem)
    for row in _tmp_rows:
        _line = row.copy()
        if 'status_ip' in row:
            record_host = row['status_ip']
            _update = reparse_record_from_exports(record_host)
            _line.update(_update)
            _line.pop('status_ip')
            yield _line


def get_uniq_row(struct, keys):
    result = all(elem in list(struct.keys()) for elem in list(keys))
    if result:
        _tmp = '_'.join([struct[k] for k in keys])
        return _tmp.__hash__()


class NFSHeader(metaclass=Header):
    display_name = 'Search data from NFS services'
    current_day = Field('Date', ValueType.Datetime)
    host_query = Field('Search ip', ValueType.String)
    shared_path = Field('NFS path', ValueType.String)
    ip = Field('ip address', ValueType.String)
    network = Field('network address', ValueType.String)
    host = Field('host', ValueType.String)
    status = Field('raw record', ValueType.String)


class SearchDataNFS(Task):
    def __init__(self):
        super().__init__()
        self.info, self.error, self.result, self.api, self.api_key = [None] * 5

    def get_id(self):
        return 'bf51fd57-3fec-4416-9d07-905935a484b4'

    def get_display_name(self):
        return 'Explore: NFS(SSH)'

    def get_category(self):
        return 'Local tasks'

    def get_description(self):
        return 'Explore NFS resourses'

    def get_headers(self):
        return NFSHeader

    def get_enter_params(self):
        ep_coll = EnterParamCollection()
        ep_coll.add_enter_param('ips', 'IP', ValueType.String, is_array=True,
                                value_sources=[Attributes.System.IPAddress], description='IPs, networks')
        return ep_coll

    def execute(self, enter_params, result_writer, log_writer, temp_dir=None):
        ips = []
        for input_ip in set(map(lambda z: z.strip(), enter_params.ips)):
            ips.extend(reparse_ip_hosts(input_ip))

        from warnings import filterwarnings
        filterwarnings('ignore')

        ports = [111, 2049]
        targets = ((ip, port) for ip in ips for port in ports)
        lines = thread_async_nfs_one_client(targets)
        info = reparse_result_rows(lines)
        fields_table = NFSHeader.get_fields()
        for data_id in info:
            tmp = NFSHeader.create_empty()
            for field in fields_table:
                if field in data_id:
                    tmp[fields_table[field]] = data_id[field]
            result_writer.write_line(tmp, header_class=NFSHeader)


if __name__ == '__main__':
    SSH_HOST = '192.168.1.1'
    SSH_PORT = 22
    USERNAME = 'user'
    PASSWORD = 'password'

    import sys
    from warnings import filterwarnings
    filterwarnings('ignore')

    class EnterParameters:
        ips = ['192.168.1.0/24']  # ip, targets

    class ResultWriterSub:
        @staticmethod
        def write_line(line: dict, header_class: Header):
            print(','.join([str(v) for v in line.values()]))

    class LogWriterSub:
        @staticmethod
        def info(message: str, *args):
            print(message.format(args))

        @staticmethod
        def error(message: str, *args):
            print(message.format(args), file=sys.stderr)

    temp_dir = '.'

    task = SearchDataNFS()

    task.execute(EnterParameters, ResultWriterSub, LogWriterSub, temp_dir)
