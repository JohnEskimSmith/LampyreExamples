# -*- coding: utf-8 -

#
# Author: Hegusung
# https://github.com/hegusung/RPCScan
#1. Changed for request with Lampyre: Insurgent2018 (https://habr.com/ru/post/444382/)
#2. Changed for request with Lampyre: sai aka eskim.john.smith

from ipaddress import ip_address, ip_network, IPv4Network, IPv6Network, IPv4Address, IPv6Address
import collections
from string import printable
import concurrent.futures
import struct
import socket
import time
from random import randint
import datetime
import json

try:
    from ontology import (
        Task, Header, Utils, Field, ValueType, EnterParamCollection, Attributes)
except ImportError as ontology_exception:
    print('missing or invalid ontology')
    raise ontology_exception


class RPC(object):
    def __init__(self, host, port, timeout):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.client = None

    def request(self, program, program_version, procedure, data=None, message_type=0, version=2, auth=None):

        rpc_XID  = int(time.time())
        rpc_message_type = message_type # 0=call
        rpc_RPC_version = version
        rpc_program = program
        rpc_program_version = program_version
        rpc_procedure = procedure
        rpc_Verifier_Flavor = 0  # AUTH_NULL
        rpc_Verifier_Length = 0

        proto = struct.pack(
            # Remote Procedure Call
            '!LLLLLL',
            rpc_XID,
            rpc_message_type,
            rpc_RPC_version,
            rpc_program,
            rpc_program_version,
            rpc_procedure,
        )

        if auth == None: # AUTH_NULL
            proto += struct.pack(
                '!LL',
                0,
                0,
            )
        elif auth["flavor"] == 1: # AUTH_UNIX
            stamp = int(time.time())
            stamp = int(time.time()) & 0xffff
            auth_data = struct.pack(
                    "!LL",
                    stamp,
                    len(auth["machine_name"])
            )
            auth_data += auth["machine_name"].encode()
            auth_data += b'\x00'*((4-len(auth["machine_name"]) % 4)%4)
            auth_data += struct.pack(
                    "!LL",
                    auth["uid"],
                    auth["gid"],
            )
            if len(auth['aux_gid']) == 1 and auth['aux_gid'][0] == 0:
                auth_data += struct.pack("!L", 0)
            else:
                auth_data += struct.pack("!L", len(auth["aux_gid"]))
                for aux_gid in auth["aux_gid"]:
                    auth_data += struct.pack("!L", aux_gid)

            proto += struct.pack(
                '!LL',
                1,
                len(auth_data),
            )
            proto += auth_data

        else:
            raise Exception("RPC unknown auth method")

        proto += struct.pack(
            '!LL',
            rpc_Verifier_Flavor,
            rpc_Verifier_Length,
        )

        if data != None:
            proto += data

        rpc_fragment_header = 0x80000000 + len(proto)

        proto = struct.pack('!L', rpc_fragment_header) + proto

        try:
            self.client.send(proto)

            last_fragment = False
            data = b""

            while not last_fragment:
                response = self.recv()

                last_fragment = struct.unpack('!L', response[:4])[0] & 0x80000000 != 0

                data += response[4:]

            rpc = data[:24]
            (
                rpc_XID,
                rpc_Message_Type,
                rpc_Reply_State,
                rpc_Verifier_Flavor,
                rpc_Verifier_Length,
                rpc_Accept_State
            ) = struct.unpack('!LLLLLL', rpc)

            if rpc_Message_Type != 1 or rpc_Reply_State != 0 or rpc_Accept_State != 0:
                raise Exception("RPC protocol error")

            data = data[24:]
        except struct.error:
            pass
            # raise RPCProtocolError("incorrect struct size")
        except Exception as e:
            pass
            # raise e

        return data

    def connect(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(self.timeout)
        # if we are running as root, use a source port between 500 and 1024 (NFS security options...)
        try:
            binded = False
            while not binded:
                try:
                    random_port = randint(500, 1024)
                    self.client.bind(('',random_port))
                    binded = True
                except OSError as e:
                    if "Permission denied" in str(e):
                        break
        except PermissionError as e:
            pass

        self.client.connect((self.host, self.port))

    def disconnect(self):
        self.client.close()

    def recv(self):
        rpc_response = None

        rpc_response_size = b""
        while len(rpc_response_size) != 4:
            rpc_response_size = self.client.recv(4)

        if len(rpc_response_size) != 4:
            raise RPCProtocolError("incorrect recv response size: %d" % len(rpc_response_size))
        response_size = struct.unpack('!L', rpc_response_size)[0] & 0x7fffffff

        if response_size > 0x00010000: # len too high, propably an error
            raise RPCProtocolError("response_size > 0x00010000: %d" % response_size)

        rpc_response = rpc_response_size
        while len(rpc_response) < response_size:
            rpc_response = rpc_response + self.client.recv(response_size-len(rpc_response)+4)

        return rpc_response


class Portmap(RPC):
    program = 100000  # Portmap
    program_version = 2

    def null(self):
        procedure = 0 # Null

        super(Portmap, self).request(self.program, self.program_version, procedure)

        # no exception raised
        return True

    def dump(self):
        procedure = 4 # Dump

        proto = struct.pack(
            '!LL',
            self.program_version,
            procedure
        )

        portmap = super(Portmap, self).request(self.program, self.program_version, procedure, data=proto)

        rpc_map_entries = []

        if len(portmap) <= 4:  # portmap_Value_Follows + one portmap_Map_entry
            return rpc_map_entries

        portmap_Value_Follows = portmap[0:4]
        portmap_Map_Entries = portmap[4:]

        while portmap_Value_Follows == b'\x00\x00\x00\x01':
            (
                program,
                version,
                protocol,
                port
            ) = struct.unpack('!LLLL', portmap_Map_Entries[:16])
            portmap_Map_Entries = portmap_Map_Entries[16:]

            if protocol == 0x06:
                protocol = 'tcp'
            elif protocol == 0x11:
                protocol = 'udp'
            else:
                protocol = 'unknown'.format(protocol)

            _ = {
                'program': program, 'version': version,
                'protocol': protocol, 'port': port
            }
            if _ not in rpc_map_entries:
                rpc_map_entries.append(_)

            portmap_Value_Follows = portmap_Map_Entries[0:4]
            portmap_Map_Entries = portmap_Map_Entries[4:]


        return rpc_map_entries

    def getport(self, getport_program, getport_program_version, getport_protocol=6):
        # RPC
        program = 100000 # Portmap
        program_version = 2
        procedure = 3 # GetPort

        # GetPort
        getport_port = 0

        proto = struct.pack(
            '!LLLL',
            getport_program,
            getport_program_version,
            getport_protocol,
            getport_port
        )

        getport = super(Portmap, self).request(program, program_version, procedure, data=proto)

        (port,) = struct.unpack('!L', getport)
        return port


class NFSAccessError(Exception):
    pass


class NFS(RPC):
    program = 100003
    program_version = 3

    def null(self):
        procedure = 0 # Null

        super(NFS, self).request(self.program, self.program_version, procedure)

        # no exception raised
        return True

    def lookup(self, dir_handle, file_folder, auth=None):
        if type(dir_handle) != bytes:
            raise Exception("file_id should be bytes")

        procedure = 3 # Lookup

        data = struct.pack('!L', len(dir_handle))
        data += dir_handle
        data += b'\x00'*((4-len(dir_handle) % 4)%4)

        data += struct.pack('!L', len(file_folder))
        data += file_folder.encode()
        data += b'\x00'*((4-len(file_folder) % 4)%4)

        data = super(NFS, self).request(self.program, self.program_version, procedure, data=data, auth=auth)

        nfs_status = struct.unpack('!L', data[:4])[0]
        data = data[4:]

        if nfs_status != 0:
            raise NFSAccessError("Error: %d" % nfs_status)

        file_handle_len = struct.unpack("!L", data[:4])[0]
        data = data[4:]

        file_handle = data[:file_handle_len]
        data = data[file_handle_len:]
        data = data[(4-file_handle_len % 4)%4:]

        value_follows = data[:4]
        data = data[4:]

        if value_follows == b'\x00\x00\x00\x01':
            attributes = data[:84]
            data = data[84:]

            (file_type, mode, ulink, uid, gid, file_size) = struct.unpack('!LLLLLL', attributes[:24])
            # File types:
            # 1: Regular file
            # 2: Directory
            # 5: Symbolic link
        else:
            file_type = None
            file_size = None

        return {
            "file_handle": file_handle,
            "file_type": file_type,
            "file_size": file_size,
        }

    def read(self, file_handle, auth=None, offset=0, chunk_count=1024*1024):
        if type(file_handle) != bytes:
            raise Exception("file_id should be bytes")

        procedure = 6 # Read

        data = struct.pack('!L', len(file_handle))
        data += file_handle
        data += b'\x00'*((4-len(file_handle) % 4)%4)
        data += struct.pack('!QL', offset, chunk_count)

        data = super(NFS, self).request(self.program, self.program_version, procedure, data=data, auth=auth)

        nfs_status = struct.unpack('!L', data[:4])[0]
        data = data[4:]

        if nfs_status != 0:
            raise NFSAccessError("Error: %d" % nfs_status)

        value_follows = data[:4]
        data = data[4:]

        if value_follows == b'\x00\x00\x00\x01':
            attributes = data[:84]
            data = data[84:]

            (file_type, mode, ulink, uid, gid, file_size) = struct.unpack('!LLLLLL', attributes[:24])
            # File types:
            # 1: Regular file
            # 2: Directory
            # 5: Symbolic link
        else:
            file_type = None
            file_size = None

        (count, EOF) = struct.unpack('!LL', data[:8])
        data = data[8:]

        file_len = struct.unpack("!L", data[:4])[0]
        data = data[4:]
        file_data = data[:file_len]
        data = data[file_len:]
        data = data[(4-file_len % 4)%4:]

        if len(file_data) != count:
            raise Exception("File size mismatch")

        if EOF == 0:
            file_data += self.read(file_handle, auth=auth, offset=offset+len(file_data))

        return file_data

    def readdirplus(self, dir_handle, cookie=0, auth=None):
        # file_id should by bytes
        if type(dir_handle) != bytes:
            raise Exception("file_id should be bytes")

        procedure = 17 # Export

        dircount = 4096
        maxcount = dircount*8

        data = struct.pack('!L', len(dir_handle))
        data += dir_handle
        data += struct.pack('!Q', cookie)
        data += struct.pack('!QLL', 0, dircount, maxcount)

        data = super(NFS, self).request(self.program, self.program_version, procedure, data=data, auth=auth)

        nfs_status = struct.unpack('!L', data[:4])[0]
        data = data[4:]

        if nfs_status != 0:
            raise NFSAccessError("Error: %d" % nfs_status)

        dir_attributes = data[:88]
        data = data[88:]

        opaque_data = data[:8]
        data = data[8:]

        contents = []
        last_cookie = 0

        value_follows = data[:4]
        data = data[4:]
        while value_follows == b'\x00\x00\x00\x01':
            file_id = struct.unpack("!Q", data[:8])[0]
            data = data[8:]

            name_len = struct.unpack("!L", data[:4])[0]
            data = data[4:]

            name = data[:name_len].decode()
            data = data[name_len:]
            data = data[(4-name_len % 4)%4:]

            cookie = struct.unpack("!Q", data[:8])[0]
            last_cookie = cookie
            data = data[8:]

            value_follows = data[:4]
            data = data[4:]

            if value_follows == b'\x00\x00\x00\x01':
                attributes = data[:84]
                data = data[84:]

                (file_type, mode, ulink, uid, gid, file_size) = struct.unpack('!LLLLLL', attributes[:24])
                # File types:
                # 1: Regular file
                # 2: Directory
                # 5: Symbolic link
            else:
                file_type = None
                file_size = None

            handle_value_follows = data[:4]
            data = data[4:]

            if handle_value_follows == b'\x00\x00\x00\x01':
                len_file_handle = struct.unpack('!L', data[:4])[0]
                data = data[4:]
                file_handle = data[:len_file_handle]
                data = data[len_file_handle:]
            else:
                file_handle = None

            contents.append({
                "name": name,
                "file_type": file_type,
                "cookie": cookie,
                "file_id": file_id,
                "file_handle": file_handle,
                "file_size": file_size,
            })

            value_follows = data[:4]
            data = data[4:]

        EOF = data[:4]

        if EOF == b'\x00\x00\x00\x00':
            self.readdirplus(dir_handle, cookie=last_cookie, auth=auth)

        return contents


class RPCProtocolError(Exception):
    pass


class MountAccessError(Exception):
    pass


class Mount(RPC):
    program = 100005
    program_version = 3

    def null(self, auth=None):
        procedure = 0 # Null

        super(Mount, self).request(self.program, self.program_version, procedure, auth=auth)

        # no exception raised
        return True

    def mnt(self, path, auth=None):
        procedure = 1

        data = struct.pack('!L', len(path))
        data += path.encode()
        data += b'\x00'*((4-len(path) % 4)%4)

        data = super(Mount, self).request(self.program, self.program_version, procedure, data=data, auth=auth)

        status = struct.unpack('!L', data[:4])[0]
        data = data[4:]

        if status != 0:
            raise MountAccessError("MNT error: %d" % status)

        len_file_handle = struct.unpack('!L', data[:4])[0]
        data = data[4:]
        file_handle = data[:len_file_handle]
        data = data[len_file_handle:]

        flavors = []
        flavors_nb = struct.unpack('!L', data[:4])[0]
        data = data[4:]
        for _ in range(flavors_nb):
            flavor = struct.unpack('!L', data[:4])[0]
            flavors.append(flavor)
            data = data[4:]

        return {
            "file_handle": file_handle,
            "flavors": flavors,
        }


    def export(self):
        # RPC
        procedure = 5 # Export

        export = super(Mount, self).request(self.program, self.program_version, procedure)
        exports = []

        export_Value_Follows = export[:4]
        export_Entries = export[4:]


        while export_Value_Follows == b'\x00\x00\x00\x01':

            (path_len,) = struct.unpack('!L', export_Entries[:4])
            export_Entries = export_Entries[4:]

            path = export_Entries[:path_len].decode('utf-8')

            export_Entries = export_Entries[path_len:]

            export_Entries = export_Entries[(4-path_len % 4)%4:]

            group_value_follows = export_Entries[:4]
            export_Entries = export_Entries[4:]

            authorized_ip = []

            while group_value_follows == b'\x00\x00\x00\x01':

                (ip_len,) = struct.unpack('!L', export_Entries[:4])

                export_Entries = export_Entries[4:]

                ip = export_Entries[:ip_len].decode('utf-8')
                authorized_ip.append(ip)

                export_Entries = export_Entries[ip_len:]

                export_Entries = export_Entries[(4-ip_len % 4)%4:]

                group_value_follows = export_Entries[:4]
                export_Entries = export_Entries[4:]

            if len(authorized_ip) == 0:
                exports.append({
                    "path": path,
                    "authorized": ['(everyone)']})
            else: exports.append({
                "path": path,
                "authorized": authorized_ip})
            export_Value_Follows = export_Entries[:4]
            export_Entries = export_Entries[4:]


        return exports


def showmount(host, port, timeout):
    try:
        portmap = Portmap(host, port, timeout)
        portmap.connect()
        port = portmap.getport(Mount.program, Mount.program_version)

        mount = Mount(host, port, timeout)
        mount.connect()
        check = False
        try:
            exports = mount.export()
            check = True
        except:
            mount.disconnect()
            portmap.disconnect()

        if check:
            mount.disconnect()
            portmap.disconnect()
            return exports
    except:
        pass


def reparse_record_from_exports(record_host, unpack_network):
    add_block = {}
    _tmp = None
    add_block['ipv4'] = []
    add_block['ipv6'] = []
    if '/' in record_host and ':' not in record_host:
        try:
            add_block['network_v4'] = str(IPv4Network(record_host))
            if unpack_network:
                add_block['ipv4'] = [_ip for _ip in map(str, _tmp)]
            else:
                add_block['ipv4'] = [str(IPv4Network(record_host)[0])]
        except:
            try:
                _ip = record_host.split('/')[0]
                _ip = str(IPv4Address(_ip))
                add_block['ipv4'].append(_ip)
            except:
                pass
    elif '/' in record_host and ':' in record_host:
        try:
            add_block['network_v6'] = str(IPv6Network(record_host))
        except:
            pass
    elif '/' not in record_host and ':' in record_host:
        try:
            add_block['ipv6'].append(str(IPv6Address(record_host)))
        except:
            pass
    else:
        try:
            add_block['ipv4'].append(str(IPv4Address(record_host)))
        except:
            if 'everyone' not in record_host and record_host != '*' and record_host != 'unknown':
                if all(c in printable for c in record_host):
                    add_block['host'] = record_host

    add_block['status'] = record_host
    result = []
    if len(add_block['ipv6']) > 0:
        add_block['ipv6'] = add_block['ipv6'][0]
        result.append(add_block)
    else:
        add_block['ipv6'] = ''
    if len(add_block['ipv4']) == 0:
        add_block['ipv4'] = ''
    else:
        for ipv4 in add_block['ipv4']:
            _c = add_block.copy()
            _c['ipv4'] = ipv4
            result.append(_c)
    if len(add_block['ipv4']) ==0 and len(add_block['ipv6']) == 0:
        result.append(add_block)
    return result


def process_get_nfs(host, port, unpack_network, timeout, actions, uid, gid, auth_hostname, recurse, lg):
    try:
        portmap = Portmap(host, 111, timeout)
        portmap.connect()
        res = portmap.null()
        portmap.disconnect()
        if res:
            if "list_mounts" in actions:
                iter_shomount = showmount(host, port, timeout)
                if iter_shomount:
                    for item in iter_shomount:
                        current_day = datetime.datetime.now().replace(microsecond=0)
                        host_query = host
                        _result = {'current_day': current_day,
                                   'host_query': host_query,
                                   'shared_path': item["path"]}
                        for auth_data in item["authorized"]:
                            for line in reparse_record_from_exports(auth_data, unpack_network):
                                _result.update(line)
                                yield _result

    except OSError:
        pass
    except Exception as e:
        print("%s:%d Exception %s:%s" % (host, port, type(e), e))
        # raise e


# ---- change Insurgent2018
def is_open_port(ip_port, GLOBAL_TIMEOUT_CHECK=3):
    ip, port = ip_port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(GLOBAL_TIMEOUT_CHECK)
    try:
        s.connect((ip, int(port)))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except:
        return False


def reparse_ip_hosts(hosts):
    need_hosts = []
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
                _tmp = list(map(str, ip_network(host)))
            except ValueError:
                pass
        else:
            try:
                _tmp = [str(ip_address(host))]
            except ValueError:
                pass
        if _tmp:
            need_hosts.extend(_tmp)
    return need_hosts


# scans for open ports, # like ping
def async_check_hosts_ports(list_ip_port, lg, timeout=3, threads=256):
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        future_rows = {executor.submit(is_open_port, host_port, timeout):
                           host_port for host_port in list_ip_port}
        for future in concurrent.futures.as_completed(future_rows):
            server_try = future_rows[future]
            result = future.result()
            if result:
                lg.info(f'online: {server_try}')
                yield server_try


def return_list_ip(in_ips, lg):  # list
    ips = []
    for input_ip in set(map(lambda z: z.strip(), in_ips)):
        ips.extend(reparse_ip_hosts(input_ip))
    ports = [111, 2049]
    targets = ((ip, port) for ip in ips for port in ports)
    need_ips = async_check_hosts_ports(targets, lg)  # like ping
    return need_ips


def main_scan(in_ips, lg):  # list
    current_targets = (ip for ip, port in return_list_ip(in_ips, lg))
    return current_targets



def main_nfs(targets, unpack_network, log_writer, _timeout=10, workers=32):
    # set default values
    port = 111
    timeout = _timeout
    actions = ["list_mounts"]
    uid = 0
    gid = 0
    hostname = 'nfsclient'
    recurse = 1
    i = 1
    c_targets = targets.__len__()
    log_writer.info(f'all targets:{c_targets}')
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_rows = {executor.submit(process_get_nfs, ip, port,  unpack_network, timeout, actions, uid, gid, hostname, recurse, log_writer):
                           ip for ip in targets}

        for future in concurrent.futures.as_completed(future_rows):
            ip = future_rows[future]
            result = future.result()
            if result:
                _tmp = [line for line in result]
                results.extend(_tmp)
                if len(_tmp) > 0:
                    log_writer.info(f'{i} from({c_targets}). done host:{ip}')
                else:
                    log_writer.info(f"{i} from({c_targets}). not found:{ip}")
            i += 1
    return results

class NFSHeader(metaclass=Header):
    display_name = 'Search data from NFS service'

    current_day = Field('Date', ValueType.Datetime)
    host_query = Field('Search ip', ValueType.String)
    shared_path = Field('NFS path', ValueType.String)
    ipv4 = Field('IPv4 address', ValueType.String)
    ipv6 = Field('IPv6 address', ValueType.String)
    network_v4 = Field('network(IPv4) address', ValueType.String)
    network_v6 = Field('network(IPv6) address', ValueType.String)
    host = Field('host', ValueType.String)
    status = Field('raw record', ValueType.String)


class SearchDataNFS(Task):
    def __init__(self):
        super().__init__()
        self.info, self.error, self.result, self.api, self.api_key = [None] * 5

    def get_id(self):
        return '6866f257-794a-4572-a0cb-daf6cef64fa7'

    def get_display_name(self):
        return 'Explore: NFS(native)'

    def get_category(self):
        return 'Local tasks'

    def get_description(self):
        return 'Explore NFS resourses'

    def get_weight_function(self):
        return 'ips'

    def get_headers(self):
        return NFSHeader

    def get_enter_params(self):
        ep_coll = EnterParamCollection()
        ep_coll.add_enter_param('ips', 'IP', ValueType.String, is_array=True, description="""IPs, networks, e.g.:\n1. 192.168.1.1\n2. 192.168.1.0/24""")
        ep_coll.add_enter_param('unpack_network', 'Unpack network record', ValueType.Boolean, default_value=False)
        ep_coll.add_enter_param('timeout', 'timeout', ValueType.Integer, is_array=False,
                                predefined_values=[3, 7, 10, 15], default_value=7,
                                description='timeout, int value')
        ep_coll.add_enter_param('max_threads', 'Max. threads', ValueType.Integer, predefined_values= [8, 16, 32],
                                default_value=8, required=True)

        return ep_coll

    def execute(self, enter_params, result_writer, log_writer, temp_dir=None):
        unpack_network = enter_params.unpack_network
        max_threads = enter_params.max_threads
        scan_network = set(map(lambda z:z.strip(), enter_params.ips))

        time_for_connect = enter_params.timeout
        from warnings import filterwarnings
        filterwarnings("ignore")
        like_cache = []
        targets = set(list(main_scan(scan_network, log_writer)))
        fields_table = NFSHeader.get_fields()
        all_nfs_shares = main_nfs(targets, unpack_network, log_writer, _timeout=time_for_connect, workers=max_threads)
        for row in all_nfs_shares:
            # like cache
            _tmp_c = row.copy()
            _tmp_c.pop('current_day')
            _c = json.dumps(_tmp_c)
            # ---------
            if _c not in like_cache:
                like_cache.append(_c)
                tmp = NFSHeader.create_empty()
                for field in fields_table:
                    if field in row:
                        tmp[fields_table[field]] = row[field]
                result_writer.write_line(tmp, header_class=NFSHeader)


if __name__ == '__main__':

    import sys
    from warnings import filterwarnings
    filterwarnings("ignore")

    class EnterParameters:
        ips = ['46.32.248.0/24']
        # ips = ['46.32.248.187', '46.32.248.141']
        unpack_network = False
        max_threads = 16
        timeout = 5

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

    SearchDataNFS().execute(EnterParameters, WriterFake, WriterFake, None)
