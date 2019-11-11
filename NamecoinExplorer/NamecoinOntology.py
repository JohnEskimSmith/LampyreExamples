# -*- coding: utf8 -*-
__author__ = 'sai'
from lighthouse import *
from os.path import join as join_path

NAME = 'Namecoin ontology'
ONTOLOGY_ID = '94fe7a33-89c0-499b-946c-4b4523f59d61'

try:
    from ontology import (Object, Link, Attribute,
        Task, Header, HeaderCollection, Utils, Field, ValueType, SchemaLink, SchemaObject, Condition, Operations, Macro,
        MacroCollection, Schema, EnterParamCollection, SchemaCollection, GraphMappingFlags, BinaryType, Constants,
        Attributes, IP, Domain, IPToDomain)
except ImportError as ontology_exception:
    print('...missing or invalid ontology')
    raise ontology_exception


class NamecoinTXnExplorer_in(metaclass=Header):
    display_name = 'Namecoin Explorer(TX) Input'
    date_time = Field('Date and time Block', ValueType.Datetime)
    hash_block = Field('hash_block', ValueType.String)
    txid = Field('txid', ValueType.String)
    short_txid = Field('Short txid(8)', ValueType.String)
    txid_in =  Field('vin txid', ValueType.String)
    short_txid_in = Field('Short vin txid(8)', ValueType.String)


class NamecoinTXnExplorer_out(metaclass=Header):
    display_name = 'Namecoin Explorer(TX) Output'
    date_time = Field('Date and time Block', ValueType.Datetime)
    hash_block = Field('hash_block', ValueType.String)
    txid = Field('txid', ValueType.String)
    short_txid = Field('Short txid(8)', ValueType.String)
    address =  Field('address', ValueType.String)
    short_address = Field('Short address(10)', ValueType.String)
    value = Field('Value(coins)', ValueType.Float)
    nameOp = Field('Op', ValueType.String)
    raw_name = Field('Raw name', ValueType.String)
    value_scripts = Field('Value', ValueType.String)
    namecoin_domain = Field('Domain(Namecoin)', ValueType.String)
    ip = Field('ip', ValueType.String)


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
    short_txid = Field('Short txid(8)', ValueType.String)


class UnionTxAddress(metaclass=Header):
    display_name = f'Namecoin Chain: Tx and Address'
    date_time = Field('Date and time Block', ValueType.Datetime)
    txid = Field('txid', ValueType.String)
    short_txid = Field('Short txid(8)', ValueType.String)
    SymbolDirection = Field('Direction', ValueType.String)
    address = Field('address', ValueType.String)
    short_address = Field('Short address(8)', ValueType.String)
    value = Field('Value(coins, NMC)', ValueType.Float)
    direction = Field('Direction Integer', ValueType.Integer)


class NamecoinTXid(metaclass=Object):
    name = "Namecoin transaction"
    txid = Attribute("Transaction id", ValueType.String)
    txid_short = Attribute("Transaction id (short)", ValueType.String)
    IdentAttrs = [txid]
    CaptionAttrs = [txid_short]
    Image = Utils.base64string(r"images\TX.png")


class NamecoinAddress(metaclass=Object):
    name = "Namecoin address"
    namecoint_address = Attribute("Namecoin address", ValueType.String)
    namecoint_address_short = Attribute("Namecoin address (short)", ValueType.String)
    IdentAttrs = [namecoint_address]
    CaptionAttrs = [namecoint_address_short]
    Image = Utils.base64string(r"images\namecoin.png")


class NamecoinTXidToNamecoinTXid(metaclass=Link):
    name = Utils.make_link_name(NamecoinTXid, NamecoinTXid)
    DateTime = Attributes.System.Datetime
    CaptionAttrs = [DateTime]
    Begin = NamecoinTXid
    End = NamecoinTXid


class NamecoinTXidToDomain(metaclass=Link):
    name = Utils.make_link_name(NamecoinTXid, Domain)
    DateTime = Attributes.System.Datetime
    CaptionAttrs = [DateTime]
    Begin = NamecoinTXid
    End = Domain


class NamecoinTXidToIP(metaclass=Link):
    name = Utils.make_link_name(NamecoinTXid, IP)
    DateTime = Attributes.System.Datetime
    CaptionAttrs = [DateTime]
    Begin = NamecoinTXid
    End = IP


class NamecoinTXidToAddress(metaclass=Link):
    name = Utils.make_link_name(NamecoinTXid, NamecoinAddress)
    DateTime = Attributes.System.Datetime
    Value = Attribute("Coins(Value)", ValueType.Float)
    Domain = Attributes.System.Domain
    Operation = Attributes.System.Description
    CaptionAttrs = [Value, Domain, Operation, DateTime]
    Begin = NamecoinTXid
    End = NamecoinAddress


class NamecoinAddressToIP(metaclass=Link):
    name = Utils.make_link_name(NamecoinAddress, IP)
    DateTime = Attributes.System.Datetime
    CaptionAttrs = [DateTime]
    Begin = NamecoinAddress
    End = IP


class NamecoinAddressToDomain(metaclass=Link):
    name = Utils.make_link_name(NamecoinAddress, Domain)
    DateTime = Attributes.System.Datetime
    CaptionAttrs = [DateTime]
    Begin = NamecoinAddress
    End = Domain


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

