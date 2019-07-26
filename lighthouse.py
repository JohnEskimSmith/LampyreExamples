import abc
import copy
import csv
import sys
import base64
import codecs
import collections
import itertools
import os
import datetime

from collections import defaultdict
from random import randint
from typing import Any, Tuple, Dict, List, Set, Union, Iterable
from warnings import warn


__all__ = ['Utils', 'BinaryType', 'ValueType', 'ValueSource', 'Field', 'EnterParamField', 'EnterParamCollection',
           'Header', 'HeaderCollection', 'Condition', 'Operations', 'GraphMappingFlags', 'GisMappingFlags', 'UnionMode',
           'Schema', 'SchemaCollection', 'Object', 'Link', 'SchemaObject', 'SchemaLink', 'SchemaScope', 'Attribute',
           'Macro', 'MacroCollection', 'Task', 'ResultWriter', 'LogWriter', 'RelativeDate', 'ReferencePoint',
           'Localization', 'LocalizationCulture', 'LocalizationScopes', 'TaskLocalizationItems']


PATHS_ROOT = ''

_mapping_type = Union[Dict['Attribute', Union['Field', List['Field']]], 'Header']


class Utils:
    """
    Miscellaneous utils class
    """

    @classmethod
    def base64string(cls, path: str) -> str:
        """
        Gets base64 string from given file. Use this to set image properties

        :param path: path to file
        :return: base64 string
        """

        try:
            with open(os.path.join(PATHS_ROOT, path), 'rb') as file:
                return cls.base64string_from_bytes(file.read())
        except:
            return ''

    @classmethod
    def base64string_from_bytes(cls, obj: bytes) -> str:
        """
        Gets base64 string from bytes object

        :param obj: resource bytes
        :return: base64 string
        """
        encoded_image = base64.b64encode(obj)
        return codecs.decode(encoded_image)


class _Checks:
    @staticmethod
    def check_arguments(arg_type: Any = None, **kwargs):
        """
        Checks method arguments (for internal use)

        :param arg_type: expected type
        :param kwargs: **{arg_name: arg_value}
        """
        for k, v in kwargs.items():
            if v is None:
                raise Exception(f'{k} can\'t be None')
            elif arg_type is str and v == '':
                raise Exception(f'{k} can\'t be an empty string')
            elif arg_type and not isinstance(v, arg_type):
                raise TypeError(f'{k} must be instance of {arg_type}')

    @staticmethod
    def validate_type(value: str):
        """
        Checks if argument is valid ValueType
        """
        if value not in ValueType.values():
            raise Exception(f'{value} is not a valid ValueType')

    @staticmethod
    def validate_binary_type(value: str):
        """
        Checks if argument is valid BinaryType
        """
        if value not in {'none'}.union(BinaryType.values()):
            raise Exception(f'{value} is not a valid BinaryType')

    @staticmethod
    def validate_operation(operation: str):
        """
        Checks if argument is valid Operations
        """
        if operation not in Operations.values():
                raise Exception(f'{operation} is not a valid Operation')

    @staticmethod
    def validate_mapping_flag(flag: str):
        """
        Checks if argument is valid mapping flag
        """
        if flag not in GraphMappingFlags.values().union(GisMappingFlags.values()):
            raise Exception(f'{flag} is not a valid mapping flag')

    @staticmethod
    def validate_system_name(system_name: str):
        """
        Checks if system name starts with alpha and contains only allowed characters
        """
        def valid_symbol(symbol):
            return symbol == '_' or symbol.isdigit() or symbol.isalpha()
        _Checks.check_arguments(str, system_name=system_name)
        if not system_name[0].isalpha():
            raise Exception(f'system name must begin with alphabetic symbol, {system_name} given')
        for index, character in enumerate(system_name[1:], start=1):
            if not valid_symbol(character):
                raise Exception(f'invalid symbol {character} in system name at {index}: {system_name}')


# region Enums

class BinaryType:
    """
    Defines type of binary fields
    """
    Image = 'image'
    Color = 'color'

    @classmethod
    def values(cls) -> Set[str]:
        return {cls.Image, cls.Color}


class ValueType:
    """
    Defines the only allowed types for enter parameters, header fields, etc.
    """
    Boolean = 'boolean'
    Integer = 'integer'
    Float = 'double'
    String = 'string'
    Datetime = 'datetime'

    @classmethod
    def values(cls) -> Set[str]:
        return {cls.Boolean, cls.Integer, cls.Float, cls.String, cls.Datetime}


class ValueSource:
    """
    Describes value source of attribute for schema extensions
    """
    def __init__(self, source: Union[str, 'ValueSource', 'Attribute'], param_switch: str = None,
                 value_switch: Any = None):
        """
        Creates ValueSource instance from name or from other ValueSource

        :param source: name of attribute, Attribute or ValueSource object
        :param param_switch: system_name of enterparam to change
        :param value_switch: change enterparam to this value
        """
        if isinstance(source, ValueSource):
            other = source
            self._name = other.name
            self._param_switch = other.param_switch
            self._value_switch = other.value_switch
        elif isinstance(source, Attribute):
            _Checks.check_arguments(arg_type=Attribute, source=source)
            self._name = source.name
            self._param_switch = str(param_switch) if param_switch else ''
            self._value_switch = value_switch
        elif isinstance(source, str):
            _Checks.check_arguments(arg_type=str, source=source)
            self._name = source
            self._param_switch = str(param_switch) if param_switch else ''
            self._value_switch = value_switch
        else:
            raise Exception('source must be str, Attribute or ValueSource')

    @property
    def name(self) -> str:
        return self._name

    @property
    def param_switch(self) -> str:
        return self._param_switch

    @property
    def value_switch(self) -> str:
        return self._value_switch

    def to_json(self) -> Dict[str, Any]:
        return {k.strip('_'): v for k, v in self.__dict__.items()}


class Operations:
    """
    Defines basic logical operations for Condition class
    """
    Equals = 'Equals'
    NotEqual = 'NotEqual'
    Contains = 'Contains'
    NotContain = 'NotContain'
    StartsWith = 'StartsWith'
    EndsWith = 'EndsWith'

    @classmethod
    def values(cls) -> Set[str]:
        return {cls.Equals, cls.NotEqual, cls.Contains, cls.NotContain, cls.StartsWith, cls.EndsWith}


class GraphMappingFlags:
    """
    Defines mapping flags for schema Macro
    """
    Completely = 'Completely'
    Skeleton = 'Skeleton'

    @classmethod
    def values(cls) -> Set[str]:
        return {cls.Completely, cls.Skeleton}


class GisMappingFlags:
    """
    Defines mapping flags for gis Macro
    """
    Path = 'Path'
    Heatmap = 'Heatmap'
    Instances = 'Instances'

    @classmethod
    def values(cls) -> Set[str]:
        return {cls.Path, cls.Heatmap, cls.Instances}


class UnionMode:
    """
    Defines union mode between multiple Conditions ("And", "Or")
    """
    And = 'And'
    Or = 'Or'

    @classmethod
    def values(cls) -> Set[str]:
        return {cls.And, cls.Or}


class TaskLocalizationItems:
    """
    All values in 'Task' scope, that can be localized
    """
    DisplayName = 'display_name'
    Description = 'description'
    Category = 'category'


class LocalizationScopes:
    """
    Scopes, available for manual add into culture
    """
    Task = 'task'
    Headers = 'headers'
    Schemas = 'schemas'
    Macros = 'macros'
    EnterParams = 'enter_params'
    EnterParamDescriptions = 'enter_param_descriptions'
    EnterParamCategories = 'enter_param_categories'
    MacroCategories = 'macro_categories'
    SchemaCategories = 'schema_categories'
    Fields = 'fields'
    Objects = 'objects'
    Links = 'links'
    Attributes = 'attributes'


class SchemaScope:
    Graph = 'graph'
    GIS = 'gis'
    Document = 'document'

    @classmethod
    def values(cls) -> Set[str]:
        return {cls.Graph, cls.GIS, cls.Document}
# endregion


class Field:
    """
    Describes field in result table header. Base for EnterParamField
    """

    def __init__(self, display_name: str, type: str, binary_type: str = 'none', system_name: str = ''):
        """
        :param display_name: field name to show
        :param type: field ValueType
        :param binary_type: type of field (if binary)
        """

        _Checks.check_arguments(arg_type=str, display_name=display_name)
        _Checks.validate_type(type)
        _Checks.validate_binary_type(binary_type)
        if system_name:  # if empty in constructor, will be set in header init
            _Checks.validate_system_name(system_name)
        self._system_name = system_name
        self._display_name = display_name
        self._type = type if binary_type == 'none' else ValueType.String
        self._binary_type = binary_type

    def __repr__(self):
        return f'system name: {self._system_name}; display name: {self._display_name}; type: {self._type}'

    @property
    def system_name(self) -> str:
        return self._system_name

    @property
    def display_name(self) -> str:
        return self._display_name

    @property
    def type(self) -> str:
        return self._type

    @property
    def binary_type(self) -> Union[str, None]:
        try:
            return self._binary_type
        except AttributeError:
            return None

    def set_system_name(self, name: str):
        _Checks.check_arguments(arg_type=str, name=name)
        self._system_name = name

    def to_json(self) -> Dict[str, Any]:
        return {k.strip('_'): v for k, v in self.__dict__.items()}


class Condition:
    """
    Defines condition, leading to object or link appearance in result graph.
    Example: Condition("name", Operation.StartsWith, "A")
    """

    def __init__(self, column: 'Field', operation: str, operand: Any):
        """
        Creates Condition instance

        :param Field column: column in header (main operand)
        :param str operation: (Operations) logical operation
        :param operand: any of ValueType, secondary operand for condition
        """
        _Checks.check_arguments(arg_type=Field, column=column)
        _Checks.validate_operation(operation)
        self._column = column.system_name
        self._operation = operation
        self._operand = operand

    def __repr__(self):
        return f'{self._column} {self._operation} {self._operand}'

    def to_json(self) -> Dict[str, Any]:
        return {k.strip('_'): v for k, v in self.__dict__.items()}


class EnterParamField(Field):
    """
    Enter parameter for task
    """

    def __init__(self, system_name, display_name, type, *, is_array: bool = False, required: bool = False,
                 required_group: str = '', geo_json: bool = False, file_path: bool = False, default_value: Any = None,
                 predefined_values: List[Any] = None, value_sources: List[Union[ValueSource, str, 'Attribute']] = None,
                 category: str = None, description: str = None):
        """
        Creates instance of enter parameter field

        :param system_name: field system name
        :param display_name: field name to show
        :param type: field ValueType
        :param is_array: is array of values instead of single value (only for string parameters)
        :param required: is required parameter
        :param required_group: at least one of parameters in group should be filled
        :param geo_json: is Geojson
        :param file_path: True if field is a path to a file
        :param default_value: default value, depending on ValueType
        :param list predefined_values: [Any, ...], list of predefined field values
        :param list value_sources: [ValueSource, ...], list of value sources
        :param str category: category for grouping enter parameters
        :param str description: text description of enter parameter
        """
        _Checks.check_arguments(arg_type=str, system_name=system_name, display_name=display_name)
        _Checks.validate_type(type)
        super().__init__(display_name, type, system_name=system_name)
        del self._binary_type
        arg_names = {is_array: 'is_array', required: 'required', geo_json: 'geo_json', file_path: 'file_path'}

        for arg, arg_name in arg_names.items():
            if arg is not False and not isinstance(arg, bool):
                raise TypeError(f'{arg_name} should be boolean')

        self._is_array = is_array
        if self._is_array and type != ValueType.String:
            raise Exception('is_array option available only for string enter parameters')

        self._required = required
        self._required_group = required_group
        self._geo_json = geo_json
        self._file_path = file_path
        self._default_value = default_value

        if predefined_values is not None and not isinstance(predefined_values, list):
            raise TypeError('predefined_values must be a list of values')
        self._predefined_values = predefined_values

        if value_sources is not None and not isinstance(value_sources, list):
            raise TypeError('value_sources must be a list of values')
        self._set_value_sources(value_sources)

        if category is not None and not isinstance(category, str):
            raise TypeError('category must be a string')
        self._category = category

        if description is not None and not isinstance(description, str):
            raise TypeError('description must be a string')
        self._description = description

    @property
    def is_array(self) -> bool:
        return self._is_array

    def _set_value_sources(self, sources):
        self._value_sources = []
        if sources is None:
            return
        for s in sources:
            self._value_sources.append(ValueSource(s))

    def to_json(self) -> Dict[str, Any]:
        result = super(EnterParamField, self).to_json()
        try:
            result['value_sources'] = [s.to_json() for s in self._value_sources]
        except AttributeError:
            pass
        return result


class EnterParamCollection:
    """
    Ordered collection of task enter parameters
    """

    def __init__(self, *fields: EnterParamField):
        """
        Creates instance of collection
        """
        self._fields = collections.OrderedDict()

        for ep_field in fields:
            self._append(ep_field)

    def __iter__(self) -> Iterable[EnterParamField]:
        return iter(self._fields.values())

    def __len__(self):
        return len(self._fields)

    def __repr__(self):
        return ';'.join([f'{system_name}: {field.type};' for system_name, field in self._fields.items()])

    def __getitem__(self, key) -> EnterParamField:
        return self._fields[key]

    def __setitem__(self, key, value):
        raise SyntaxError('Use .add or .add_enter_param methods to add fields')

    def __contains__(self, item):
        return item in self._fields

    def add_enter_param(self, system_name, display_name, type, *, is_array: bool = False, required: bool = False,
                        required_group: str = '', geo_json: bool = False, file_path: bool = False,
                        default_value: Any = None, predefined_values: List[Any] = None,
                        value_sources: List[Union[ValueSource, str, 'Attribute']] = None, category: str = None,
                        description: str = None):
        """
        Adds new enter parameter to collection

        :param system_name: field system name; system names in collection must be unique
        :param display_name: field name to show
        :param type: field type
        :param is_array: is array of values instead of single value
        :param required: is required parameter
        :param required_group: at least one of parameters in group should be filled
        :param geo_json: is Geojson
        :param file_path: is field representing path to a file
        :param default_value: default value, depending on ValueType
        :param predefined_values: List[Any, ...], list of predefined field values
        :param value_sources: List[ValueSource, ...], list of value sources
        :param category: category for grouping enter parameters
        :param description: text description of enter parameter
        """

        self._append(EnterParamField(
            system_name, display_name, type, is_array=is_array, required=required, required_group=required_group,
            geo_json=geo_json, file_path=file_path, default_value=default_value, predefined_values=predefined_values,
            value_sources=value_sources, category=category, description=description
        ))

    def add(self, ep_field: EnterParamField):
        """
        Add EnterParamField to collection
        """
        self._append(ep_field)

    def get(self, key: str, default: Any = None) -> Union[EnterParamField, None]:
        """
        Get EnterParamField by system name

        :param key: field system name
        :param default:
        """
        return self._fields.get(key, default)

    def _append(self, ep_field):
        _Checks.check_arguments(EnterParamField, ep_field=ep_field)
        if ep_field.system_name in self._fields:
            raise Exception(f'Enter parameter already exists: {ep_field.system_name}')
        self._fields[ep_field.system_name] = ep_field

    def to_json(self) -> List[Dict[str, Any]]:
        return [field.to_json() for field in self._fields.values()]


# noinspection PyUnresolvedReferences
class Header(type):
    """
    Describes result data table header
    """
    display_name = ''

    @classmethod
    def __prepare__(mcs, name, bases):
        return collections.OrderedDict()

    def __new__(mcs, name, bases, classdict):
        for b in bases:
            if isinstance(b, Header):
                raise Exception(f'Header inheritance is not allowed: {name}')
        classdict['__fields__'] = [key for key in classdict.keys()
                                   if key not in ('__module__', '__qualname__', 'system_name', 'display_name',
                                                  '__doc__')]
        classdict['__properties__'] = {}
        for field_name in classdict['__fields__']:
            field = classdict[field_name]
            if not isinstance(field, Field):
                raise TypeError(f'Header fields must be instances of Field, {type(field)} given')
            if isinstance(field, EnterParamField):
                raise TypeError('Header fields must be instances of Field, not EnterParamField')
            if field.system_name == '':
                field.set_system_name(field_name)
        return type.__new__(mcs, name, bases, classdict)

    def __len__(self):
        return len(self.__fields__)

    def __iter__(self) -> Iterable[Field]:
        for field_name in self.__fields__:
            yield self.__dict__[field_name]

    def __repr__(self):
        name = self.display_name or self.system_name
        return f'{name}, fields: {len(self)}'

    def get_fields(self) -> collections.OrderedDict:
        """
        :return: All header fields and their names as keys, ordered
        """
        result = collections.OrderedDict()
        for key in self.__fields__:
            result[key] = self.__dict__[key]
        return result

    def create_empty(self) -> Dict[Field, Any]:
        """
        Creates empty line

        :return: Dictionary with header fields and empty values
        :rtype: dict
        """
        return {self.__dict__[f]: '' for f in self.__fields__}

    def set_property(self, field_name: str, property: str, value: Any):
        """
        Set custom header property
        """
        _Checks.check_arguments(arg_type=str, field_name=field_name, property=property)

        if field_name not in self.__properties__:
            self.__properties__[field_name] = {}
        self.__properties__[field_name][property] = value

    def to_json(self) -> Dict[str, Any]:
        return {
            'system_name': self.__name__,
            'display_name': self.display_name if self.display_name != '' else self.system_name,
            'fields': [f.to_json() for f in self.get_fields().values()],
            'properties': self.__properties__
        }

    @property
    def system_name(self) -> str:
        return self.__name__

    @property
    def fields(self) -> List[Field]:
        """
        All header fields as list
        """
        return list(self)

    @property
    def dtype(self) -> Dict[str, type]:
        """
        Dtype for pandas as dict {field.system_name: type}
        """
        types_map = {
            ValueType.String: str,
            ValueType.Integer: int,
            ValueType.Float: float,
            ValueType.Boolean: bool,
            ValueType.Datetime: str
        }

        return {field.system_name: types_map[field.type] for field in self}


class HeaderCollection:
    """
    Collection of all resulting headers in task
    """

    def __init__(self, *headers: Header):
        """
        Creates collection
        """
        self._headers = []
        self.add_headers(*headers)

    def __iter__(self):
        return iter(self._headers)

    def __len__(self):
        return len(self._headers)

    def __repr__(self):
        return '; '.join([repr(header) for header in self._headers])

    def _add_header(self, header: Header):
        _Checks.check_arguments(arg_type=Header, header=header)
        if header.system_name in [h.system_name for h in self._headers]:
            raise Exception('Header system name must be unique')
        self._headers.append(header)

    def add_headers(self, *headers: Header):
        """
        Adds multiple headers to collection
        """
        for h in headers:
            self._add_header(h)

    def to_json(self) -> List[Dict[str, Any]]:
        return [h.to_json() for h in self._headers]


# noinspection PyUnresolvedReferences
class Schema(type):
    """
    Describes graph schema, mapped to specific header, with objects and links between them
    """
    name = ''

    @classmethod
    def __prepare__(mcs, name, bases):
        return collections.OrderedDict()

    @staticmethod
    def get_json(name: str, objects: list, links: list, scopes: List[str] = None,
                 header_system_name: str = '', category='') -> Dict[str, Any]:
        result = {
            'object_properties': {},
            'link_properties': {},
            'attribute_properties': {},
            'name': name,
            'header_system_name': header_system_name,
            'objects': [o.to_json() for o in objects],
            'links': [l.to_json() for l in links],
        }

        if scopes:
            result['scopes'] = scopes

        if category:
            result['category'] = category

        def set_entity_property(entity, key, value):
            properties = result['object_properties'] if type(entity) == Object else result['link_properties']
            e_name = entity.name
            if e_name:
                if e_name in properties:
                    properties[e_name][key] = value
                else:
                    properties[e_name] = {key: value}

        def set_attribute_property(attr, key, value):
            properties = result['attribute_properties']
            if attr.name in properties:
                properties[attr.name][key] = value
            else:
                properties[attr.name] = {key: value}

        entities = set([o.type for o in objects] + [l.type for l in links])

        for entity in entities:
            # setting image properties for entities and their attributes
            if getattr(entity, 'Image', False) and entity.Image:  # check for non-empty Image property
                set_entity_property(entity, 'image', entity.Image)
            for attribute in entity.get_attributes():
                if attribute.image:
                    set_attribute_property(attribute, 'image', attribute.image)
        return result

    @staticmethod
    def process_graph(objects, links):
        graph_info = {}
        list_of_objects = []
        links_copied = []
        for obj in objects:
            if obj in graph_info:
                continue
            graph_info[obj] = len(list_of_objects)
            list_of_objects.append(obj)
        if links:
            links_copied = [l.copy() for l in links]
            for link in links_copied:
                if link.begin in graph_info:
                    left_index = graph_info[link.begin]
                else:
                    left_index = graph_info[link.begin] = len(list_of_objects)
                    list_of_objects.append(link.begin)

                if link.end in graph_info:
                    if link.end == link.begin:
                        right_index = graph_info[link.end] = len(list_of_objects)
                        list_of_objects.append(link.end)
                    else:
                        right_index = graph_info[link.end]
                else:
                    right_index = graph_info[link.end] = len(list_of_objects)
                    list_of_objects.append(link.end)

                link.begin_index = left_index
                link.end_index = right_index
                link.end_index = right_index
        return list_of_objects, links_copied

    def __new__(mcs, name, bases, classdict):
        # entities mapping check
        def check_entities(objects, links, header):
            field_system_names = {field.system_name: field for field in header.get_fields().values()}
            for entity in itertools.chain(objects, links):
                for attribute in entity.attributes:
                    for column in attribute.columns:
                        if column.system_name not in field_system_names:
                            raise Exception(f'Field {column.system_name} not presented in header {header.display_name}')

        # setting schema name
        schema_name = classdict.get('name')
        if not schema_name:
            if schema_name == '':
                raise Exception('Schema name can\'t be empty')
            classdict['name'] = name
        else:
            _Checks.check_arguments(arg_type=str, name=classdict['name'])

        # all schema entities - base and self
        entities = {k: v for k, v in classdict.items() if isinstance(v, SchemaEntity)}
        for base in bases:
            base_entities = {k: v for k, v in base.__dict__.items() if isinstance(v, SchemaEntity)}
            for attr_name, entity in base_entities.items():
                if attr_name not in classdict:
                    classdict[attr_name] = entity
                    entities[attr_name] = entity

        object_set = set([e for e in entities.values() if isinstance(e, SchemaObject)])
        link_set = set([e for e in entities.values() if isinstance(e, SchemaLink)])

        # saving objects and links to class members after filtering
        objects = classdict['__objects__'] = list(object_set)
        links = classdict['__links__'] = list(link_set)
        classdict['__scopes__'] = []
        classdict['__category__'] = None

        if len(objects) < 1:
            raise Exception('Schema must contain objects')

        # setting header (or inherit from base)
        header = None
        defined_header = classdict.get('Header')
        if defined_header and isinstance(defined_header, Header):
            header = defined_header

        for base in bases:
            if header is None:
                header = base.Header
                classdict['Header'] = header
            else:
                if header != base.Header:
                    raise Exception('Differrent headers in base schemas are not allowed')
        if header is None:
            raise Exception('Schema must be mapped to header')
        classdict['__header__'] = header

        check_entities(objects, links, header)
        classdict['__properties__'] = {}
        return type.__new__(mcs, name, (), classdict)

    def __repr__(self):
        return f'{self.name}: header: {self.__header__}, {len(self.__objects__)} objects, {len(self.__links__)} links'

    def to_json(self) -> Dict[str, Any]:
        self.__objects__, self.__links__ = Schema.process_graph(self.__objects__, self.__links__)
        return Schema.get_json(self.name, self.__objects__, self.__links__, self.__scopes__,
                               self.__header__.system_name, self.__category__)

    def get_name(self) -> str:
        return self.name

    def get_entities(self) -> Tuple[list, list]:
        return self.__objects__, self.__links__

    def set_property(self, key1: str, key2: str, value: Any):
        """
        Set custom schema property
        """
        if key1 not in self.__properties__:
            self.__properties__[key1] = {}
        self.__properties__[key1][key2] = value

    def set_scopes(self, *scopes: str):
        """
        Set applicable scopes for this schema, such as Graph, GIS, or Document - see SchemaScopes enum

        :param scopes: one of SchemaScopes
        """
        self.__scopes__ = list(set([scope for scope in scopes if scope in SchemaScope.values()]))

    def set_category(self, category: str):
        _Checks.check_arguments(str, category=category)
        self.__category__ = category


class SchemaCollection:
    """
    Collection of all task's schemas
    """

    def __init__(self, *schemas):
        """
        Creates instance of collection. Schema's names must be unique.

        :param type schemas:
        """
        self._schemas = []
        self.add_schemas(*schemas)

    def __iter__(self) -> Iterable[Schema]:
        return iter(self._schemas)

    def __len__(self):
        return len(self._schemas)

    def _add_schema(self, schema):
        _Checks.check_arguments(arg_type=Schema, schema=schema)
        if schema.name in [s.name for s in self._schemas]:
            raise Exception(f'Schema with this name already exists: {schema.name}')
        self._schemas.append(schema)

    def add_schemas(self, *schemas: Schema):
        """
        Adds schema(s) to collection.

        Throws exception if schema with such name already presented in collection (names must be unique)
        """
        for s in schemas:
            self._add_schema(s)

    def to_json(self) -> List[Dict[str, Any]]:
        return [s.to_json() for s in self._schemas]


class SchemaEntity:
    """
    Base class for SchemaObject and SchemaLink types. For internal usage
    """
    def __init__(self, entity_type: Union['Object', 'Link'], mapping: _mapping_type,
                 conditions: List[Condition] = None, condition_union_mode: str = UnionMode.And,
                 condition_ignore_case: bool = True):
        """
        Base initialization for SchemaObject or SchemaLink
        """
        if entity_type is None:
            raise Exception('Type can\'t be None')
        if not (isinstance(entity_type, Object) or isinstance(entity_type, Link)):
            raise TypeError('Schema entity type must be derivative of Object or Link')
        self._type = entity_type
        self._name = entity_type.name
        self._attributes = []
        self._conditions = []
        if conditions:
            if isinstance(conditions, list):
                for c in conditions:
                    _Checks.check_arguments(arg_type=Condition, condition=c)
                    self._conditions.append(c)
            else:
                raise TypeError('Conditions must be a list')
        self._properties = {}
        _Checks.check_arguments(arg_type=str, condition_union_mode=condition_union_mode)
        if condition_union_mode in [UnionMode.And, UnionMode.Or]:
            self._condition_union_mode = condition_union_mode
        else:
            raise Exception('Invalid condition union mode')
        _Checks.check_arguments(arg_type=bool, condition_ignore_case=condition_ignore_case)
        self._condition_ignore_case = condition_ignore_case
        type_attributes = self._type.get_attributes()
        if isinstance(mapping, dict):
            for attr in mapping:
                if not isinstance(attr, Attribute):
                    raise TypeError(f'Mapping keys must be of type Attribute, {type(attr)} given')
                if attr not in type_attributes:
                    raise Exception(f'Invalid mapping: attribute {attr.name} not found in entity type')

            for type_attr in type_attributes:
                fields = mapping.get(type_attr, [])
                attr = type_attr.clone()
                if isinstance(fields, list):
                    attr.add_columns(*fields)
                else:
                    attr.add_columns(fields)
                self._add_attribute(attr)
        elif isinstance(mapping, Header):
            header_fields = mapping.get_fields()
            for attr_name, type_attr in self._type.get_attributes_dict().items():
                attr = type_attr.clone()
                attr.add_columns(header_fields[attr_name])
                self._add_attribute(attr)
        else:
            raise TypeError('Mapping must be a dict or Header')

    def __repr__(self):
        if isinstance(self, SchemaObject):
            return f'SchemaObject: {self._type}'
        else:
            return f'SchemaLink: {self._type}'

    @property
    def name(self) -> str:
        return self._name

    @property
    def attributes(self) -> List['Attribute']:
        return copy.copy(self._attributes)

    @property
    def type(self) -> type:
        """
        :return: underlying entity type
        """
        return self._type

    def _jsonify_common(self):
        return {
            'name': self._name,
            'row_predicate_data': {
                'condition_union_mode': self._condition_union_mode,
                'ignore_case': self._condition_ignore_case,
                'conditions': [c.to_json() for c in self._conditions]
            },
            'properties': self._properties,
            'attributes': [a.to_json() for a in self._attributes]
        }

    def _add_attribute(self, attribute):
        if attribute.name in [a.name for a in self._attributes]:
            raise Exception(f'Attribute with this name already exists: {attribute.name}')
        self._attributes.append(attribute)

    def add_condition(self, column: Field, operation: str, operand: Any):
        """
        Adds new condition to object

        :param column: column in header (main operand)
        :param operation: (Operations) logical operation
        :param operand: any of ValueType, secondary operand for condition
        """
        self._conditions.append(Condition(column, operation, operand))

    def set_properties(self, **props):
        """
        Sets custom property of entity

        :param props: keys and their values, keys must be of type str
        """
        for k, v in props.items():
            self._properties[k] = v

    def to_json(self) -> Dict[str, Any]:
        return self._jsonify_common()


# noinspection PyUnresolvedReferences
class Object(type):
    """
    Custom object type for schema
    """
    @classmethod
    def __prepare__(mcs, name, bases):
        return collections.OrderedDict()

    def __new__(mcs, name, bases, classdict):
        bases_attributes = {}
        bases_idents = set()
        bases_caps = set()
        ordered_attributes = classdict['__attributes__'] = []

        # check and save bases attributes, idents and captions
        for base in bases:
            attributes = base.get_attributes_dict()
            for field_name, base_attribute in attributes.items():
                if field_name in bases_attributes:
                    known_attr = bases_attributes[field_name]
                    if known_attr.similar_to(base_attribute):
                        continue
                    else:
                        e = f'Conflicting base fields found during object inheriting: {field_name} in type {base.name}'
                        raise Exception(e)
                new_attr = base_attribute.clone()
                ordered_attributes.append(new_attr)
                bases_attributes[field_name] = new_attr
            if hasattr(base, 'IdentAttrs'):
                bases_idents.update(base.IdentAttrs)
            if hasattr(base, 'CaptionAttrs'):
                bases_caps.update(base.CaptionAttrs)

        # check and save self attributes
        replaced_attrs = {}
        for field_name, field_value in classdict.items():
            if isinstance(field_value, Attribute):
                if field_name in bases_attributes:
                    old_attr = bases_attributes[field_name]
                    old_index = ordered_attributes.index(old_attr)
                    ordered_attributes.remove(old_attr)
                    ordered_attributes.insert(old_index, field_value)
                    replaced_attrs[field_name] = old_attr
                else:
                    ordered_attributes.append(field_value)

        # adding base, non-replaced attribute fields to new class
        for base_field, base_attr in bases_attributes.items():
            if base_field not in replaced_attrs and base_field not in classdict:
                classdict[base_field] = base_attr

        # inherit or override idents and captions
        idents = classdict.get('IdentAttrs') or list(bases_idents)
        if idents:
            classdict['IdentAttrs'] = idents
        caps = classdict.get('CaptionAttrs') or list(bases_caps)
        if caps:
            classdict['CaptionAttrs'] = caps

        for special_items in [idents, caps, ordered_attributes]:
            for item in special_items:
                if not isinstance(item, Attribute):
                    raise TypeError(f'Object attributes must be instances of Attribute, {type(item)} given')

        # reset idents and captions. Check attribute names for uniqueness
        known_attributes = {}
        for attr in ordered_attributes:
            # if not isinstance(attr, Attribute):
            #     raise TypeError('Object attributes must be instances of Attribute, {} given'.format(type(attr)))
            if attr.name in known_attributes:
                raise Exception(f'More than one attribute with name {attr.name}. Names must be unique')
            else:
                known_attributes[attr.name] = attr
            for ident in idents:
                if ident.similar_to(attr):
                    attr.ident = True
            for caption in caps:
                if caption.similar_to(attr):
                    attr.caption = True

        object_name = classdict.get('name')
        if not object_name:
            if object_name == '':
                raise Exception('Object name can\'t be empty')
            classdict['name'] = object_name if object_name else name
        else:
            _Checks.check_arguments(arg_type=str, name=classdict['name'])

        for char in '.$':
            if char in classdict['name']:
                raise Exception(f'Object name can\'t contain character "{char}"')

        return type.__new__(mcs, name, (), classdict)

    def __repr__(cls):
        return f'Object: {cls.name}'

    def get_attributes(cls) -> List['Attribute']:
        """
        :return: All object attributes, ordered
        """
        return cls.__attributes__

    def get_attributes_dict(cls) -> Dict[str, 'Attribute']:
        """
        :return: Dict of attributes {class field name: attribute}
        """
        return {name: item for name, item in cls.__dict__.items() if item in cls.__attributes__}

    def schematic(cls, mapping: _mapping_type, conditions: List[Condition] = None, condition_union_mode: str = UnionMode.And,
                  condition_ignore_case: bool = True) -> 'SchemaObject':
        """
        Creates SchemaObject instance of this type on schema

        :return: SchemaObject instance of this type
        """
        return SchemaObject(cls, mapping, conditions, condition_union_mode, condition_ignore_case)

    @property
    def system_name(self) -> str:
        return self.__name__


# noinspection PyUnresolvedReferences
class Link(type):
    """
    Custom type of the link. Must contain Begin and End attributes, which are object types
    """
    @classmethod
    def __prepare__(mcs, name, bases):
        return collections.OrderedDict()

    def __new__(mcs, name, bases, classdict):
        for b in bases:
            if isinstance(b, Link):
                raise Exception(f'Link inheritance is not allowed: {name}')
        classdict['__attributes__'] = [v for key, v in classdict.items()
                                       if key not in ('__module__', '__qualname__', 'name', 'Begin', 'End', '__doc__',
                                                      'Image', 'CaptionAttrs')]

        link_name = classdict.get('name')

        begin, end = classdict.get('Begin'), classdict.get('End')
        if not begin or not end:
            raise Exception('Link must have begin and end types')
        
        if not isinstance(begin, Object):
            raise TypeError('Link begin must be Object')
        if not isinstance(end, Object):
            raise TypeError('Link end must be Object')
        
        if not link_name:
            classdict['name'] = ''  # Link names are empty by default
        else:
            _Checks.check_arguments(arg_type=str, name=classdict['name'])

        attr_names = []
        caps = classdict.get('CaptionAttrs')
        for attr in classdict['__attributes__']:
            if not isinstance(attr, Attribute):
                raise TypeError(f'Link attributes must be instances of Attribute, {type(attr)} given')
            if attr.name in attr_names:
                raise Exception(f'More than one attribute with name {attr.name}. Names must be unique')
            else:
                attr_names.append(attr.name)
            attr.ident = True
            if caps and attr in caps:
                attr.caption = True

        return type.__new__(mcs, name, bases, classdict)

    def __repr__(cls):
        return f'Link: {cls.name}; Begin: {cls.Begin.name}, End: {cls.End.name}'

    def get_attributes(cls) -> List['Attribute']:
        """
        :return: All link attributes, ordered
        """
        return cls.__attributes__

    def get_attributes_dict(cls) -> Dict[str, 'Attribute']:
        """
        :return: Dict of attributes {class field name: attribute}
        """
        return {name: item for name, item in cls.__dict__.items() if item in cls.__attributes__}

    def between(cls, begin: 'SchemaObject', end: 'SchemaObject', mapping: _mapping_type,
                conditions: List[Condition] = None, condition_union_mode: str = UnionMode.And,
                condition_ignore_case: bool = True):
        """
        Dynamically creates SchemaLink of this type between two objects on schema

        :return: SchemaLink, connecting objects
        """
        return SchemaLink(cls, begin=begin, end=end, mapping=mapping, conditions=conditions, condition_union_mode=
                          condition_union_mode, condition_ignore_case=condition_ignore_case)

    @property
    def system_name(self) -> str:
        return self.__name__


class SchemaObject(SchemaEntity):
    """
    Describes object on schema or map
    """
    def __init__(self, type: Object, mapping: _mapping_type, conditions: List[Condition] = None,
                 condition_union_mode: str = UnionMode.And, condition_ignore_case: bool = True):
        """
        Creates object on schema or map

        :param type: object type
        :param mapping: dict or Header
        :param conditions: list of conditions
        :param condition_union_mode: (UnionMode) operation between all conditions(and, or)
        :param bool condition_ignore_case: ignore operand case
        """
        super().__init__(type, mapping, conditions, condition_union_mode, condition_ignore_case)

        self._x = randint(30, 750)
        self._y = randint(30, 450)

    def to_json(self):
        properties = self._jsonify_common()
        properties['chart_location_x'] = self._x
        properties['chart_location_y'] = self._y
        return properties

    def link_to(self, other: 'SchemaObject', custom_name: str = None, generate_name: bool = False):
        """
        Create empty link between objects

        :param SchemaObject other: any SchemaObject
        :param custom_name: set a specific name to generated Link type
        :param generate_name: create conventional name for link type
        :return: link from this to other object
        :rtype: SchemaLink
        """

        if custom_name or generate_name:
            conn_symbol = '\u2192' if self.type != other.type else '\u2013'
            generated_name = ''
            if generate_name:
                generated_name = f'{self.name} {conn_symbol} {other.name}'

            dynamic_name = custom_name or generated_name

            class DynamicLink(metaclass=Link):
                name = dynamic_name

                Empty = Attribute('Emptiness', ValueType.String)

                Begin = self.type
                End = other.type

            return SchemaLink(DynamicLink, {}, self, other)

        class DynamicLink(metaclass=Link):
            Begin = self.type
            End = other.type

        return SchemaLink(DynamicLink, {}, self, other)


class SchemaLink(SchemaEntity):
    """
    Link between two objects on schema
    """

    def __init__(self, type: Link, mapping: _mapping_type, begin: SchemaObject, end: SchemaObject,
                 conditions: List[Condition] = None, condition_union_mode: str = UnionMode.And,
                 condition_ignore_case: bool = True):
        """
        Creates custom link between two objects.

        :param type: link type
        :param mapping: dict (attribute to header field(s) mapping) or Header
        :param begin: link begin object
        :param end: link end object
        :param conditions: list of conditions
        :param condition_union_mode: (UnionMode) operation between all conditions(and, or)
        :param condition_ignore_case: ignore operand case
        """
        super().__init__(type, mapping, conditions, condition_union_mode, condition_ignore_case)
        _Checks.check_arguments(arg_type=SchemaObject, begin=begin, end=end)
        if begin.type != type.Begin:
            raise TypeError('Begin type differs from Link begin type')
        if end.type != type.End:
            raise TypeError('End type differs from Link end type')
        self.begin = begin
        self.end = end
        self.begin_index = None
        self.end_index = None

    def copy(self) -> 'SchemaLink':
        """
        Creates a copy of Link and preserves begin and end objects references

        :rtype: SchemaLink
        :return: new SchemaLink, connecting same objects
        """
        clone = copy.deepcopy(self)
        clone.begin = self.begin
        clone.end = self.end
        return clone

    def to_json(self) -> Dict[str, Any]:
        if self.begin_index is None:
            warn('Begin object index not set')
        if self.end_index is None:
            warn('End object index not set')
        properties = self._jsonify_common()
        properties['begin_object_index'] = self.begin_index
        properties['end_object_index'] = self.end_index
        return properties


class Attribute:
    """
    Describes custom link or object attribute
    """

    def __init__(self, name: str, type: str, image: str = None):
        """
        Creates attribute instance

        :param str name: attribute name
        :param str type: ValueType
        :param str image: (optional) base64 string of attribute image
        """
        _Checks.check_arguments(arg_type=str, name=name, type=type)
        _Checks.validate_type(type)
        for char in '.$':
            if char in name:
                raise Exception(f'Attribute name can\'t contain character "{char}"')
        self._name = name
        self._value_type = type
        self._columns = []
        self.ident = False
        self.caption = False
        self.image = image

    def __repr__(self):
        return f'Attribute: {self.name}, ValueType: {self.value_type}'

    @property
    def name(self) -> str:
        return self._name

    @property
    def value_type(self) -> str:
        return self._value_type

    @property
    def columns(self) -> List[Field]:
        return self._columns

    def similar_to(self, other: 'Attribute') -> bool:
        """
        Compare name and ValueType

        :return: Attributes are the same (or cloned)
        """
        return self.name == other.name and self.value_type == other.value_type

    def add_columns(self, *columns: Field):
        """
        Adds column to attribute

        :param Field columns: header column
        """
        for col in columns:
            _Checks.check_arguments(arg_type=Field, column=col)
            if col.system_name not in [c.system_name for c in self._columns]:
                self._columns.append(col)

    def clone(self) -> 'Attribute':
        """
        Creates identical copy of Attribute object

        :rtype: Attribute
        :return: new Attribute object
        """
        return copy.deepcopy(self)

    def to_json(self) -> Dict[str, Any]:
        return {
            'name': self._name,
            'value_type': self._value_type,
            'columns': ';'.join([c.system_name for c in self._columns]),
            'ident': self.ident,
            'caption': self.caption
        }


class Macro:
    """
    Describes a macro for schema extensions
    """
    def __init__(self, name: str, mapping_flags: List[str] = None,
                 schemas: Union[Iterable[Schema], SchemaCollection] = None,
                 switches: Dict[Union[EnterParamField, str], Any] = None,
                 *,
                 drops: Union[Iterable[Union[EnterParamField, str]], EnterParamField, str] = None,
                 drop_except: Union[Iterable[Union[EnterParamField, str]], EnterParamField, str] = None,
                 category: str = ''):
        """
        Creates Macro instance

        :param name: macro name
        :param mapping_flags: list of mapping flags (listed in GraphMappingFlags, GisMappingFlags enums)
        :param schemas: macro schemas
        :param switches: put these values to enterparams on start.
            Example: You have a task that takes a data source (e.g. database) as a parameter and you want different
            macro for each datasource. (switches={'datasource': 'my_database_1'})
        :param drops: reset these enterparams to their defaults on start (even if they are passed by macro itself).
            This can help if macro called from an object with many attributes that are value source for task parameters,
            but you don't want to pass them all.
            Example: your task have 3 params - ip, port, and date - with value sources, but you want additional macro
            that only takes ip of the object and ignore port and date when launched from context menu of the object
            with all three attributes. (drops = ['port', 'date'])
        :param drop_except: reset all unaffected parameters except given to their defaults on start.
            (drop_except=['login', 'password']). Pass empty list to reset all parameters, that are not passed by macro.
        :param category: category name for group of macros
        """

        _Checks.check_arguments(arg_type=str, name=name)
        self._name = name
        self._mapping_flags = []
        self._schemas = []
        self._switches = {}
        self._drops = set()
        self._drop_except = set()
        self._drop_exceptions_exist = drop_except is not None
        self.category = category

        if mapping_flags:
            if not isinstance(mapping_flags, list):
                raise Exception('mapping_flags must be a list')
            self.add_mapping_flags(*mapping_flags)

        if schemas:
            self.add_schemas(*schemas)

        if switches:
            self.add_switches(switches)

        if drops:
            self.add_drops(drops)

        if drop_except:
            self.add_drop_exceptions(drop_except)

    @property
    def name(self) -> str:
        return self._name

    def _get_names(self, obj, recursive=False):
        if isinstance(obj, str):
            return obj if recursive else [obj]
        elif isinstance(obj, collections.Iterable):
            return [self._get_names(item, recursive=True) for item in obj]
        elif isinstance(obj, EnterParamField):
            return obj.system_name if recursive else [obj.system_name]
        elif isinstance(obj, Attribute) or isinstance(obj, Schema):
            return obj.name if recursive else [obj.name]
        else:
            raise TypeError(f'Unsupported type: {type(obj)}')

    def add_mapping_flags(self, *flags: str):
        """
        Adds mapping flags to a macro

        :param str flags: GraphMappingFlags or GisMappingFlags: unique mapping flags
        """
        for flag in flags:
            if flag not in self._mapping_flags:
                _Checks.validate_mapping_flag(flag)
                self._mapping_flags.append(flag)

    def add_schemas(self, *schemas: Schema):
        """
        Adds schemas names to a macro

        :param Schema schemas: unique mapping flags
        """
        for schema in schemas:
            _Checks.check_arguments(arg_type=Schema, schema=schema)
            if schema.name not in self._schemas:
                self._schemas.append(schema.name)

    def add_switches(self, values: Dict[Union[EnterParamField, str], Any]):
        """
        Define values for enterparams

        :param values: {EnterParamField or system_name: obj}
        """
        for ep, value in values.items():
            self._switches[self._get_names(ep)[0]] = value

    def add_drops(self, fields: Union[Iterable[Union[EnterParamField, str]], EnterParamField, str]):
        """
        Set which params will be dropped to default values by this macro

        :param fields: EnterParamField(s) or system_name(s)
        """
        self._drops.update(self._get_names(fields))

    def add_drop_exceptions(self, fields: Union[Iterable[Union[EnterParamField, str]], EnterParamField, str]):
        """
        Instruct macro to reset all parameters except listed at macro launch.

        :param fields:
        :return:
        """
        self._drop_except.update(self._get_names(fields))

    def to_json(self) -> Dict[str, Any]:
        result = {
            'name': self._name,
            'mapping_flags': self._mapping_flags,
            'schemas': self._schemas,
        }

        if self._drop_exceptions_exist:
            result['drop_except'] = list(self._drop_except) if self._drop_except else []

        if self._drops:
            result['drops'] = list(self._drops)

        if self._switches:
            result['switches'] = self._switches

        if self.category:
            result['category'] = self.category

        return result


class MacroCollection:
    """
    Collection of all user macros
    """

    def __init__(self, *macros: Macro):
        """
        Creates instance of MacroCollection from multiple macros

        :param macros:
        """
        self._macros = []
        self.add_macros(*macros)

    def __iter__(self):
        return iter(self._macros)

    def add_macros(self, *macros: Macro):
        """
        Adds macros to collection

        :param macros:
        """
        for macro in macros:
            if macro.name in [m.name for m in self._macros]:
                raise Exception(f'Macro with this name already exists: {macro.name}')
            self._macros.append(macro)

    def add_macro(self, name: str, mapping_flags: List[str] = None, schemas: List[Schema] = None):
        """
        Adds new macro to collection

        :param name: macro name
        :param mapping_flags: [str, ...] list of mapping flags (defined in GraphMappingFlags, GisMappingFlags)
        :param schemas: list of schemas
        """
        if name in [m.name for m in self._macros]:
            raise Exception(f'Macro with this name already exists: {name}')
        self.add_macros(Macro(name, mapping_flags, schemas))

    def to_json(self) -> List[Dict[str, Any]]:
        return [m.to_json() for m in self._macros]


class Task(metaclass=abc.ABCMeta):
    """
    Base class for implementing task. Payload goes to `execute` method
    """

    def __init__(self):
        pass

    def get_id(self) -> str:
        """
        Task unique id in uuid4 format (string)
        """
        pass

    def get_display_name(self) -> str:
        """
        Returns task display name
        """
        pass

    def get_category(self) -> str:
        """
        Returns task category
        """
        pass

    def get_description(self) -> str:
        """
        Returns task short description
        """
        pass

    @abc.abstractmethod
    def get_enter_params(self) -> EnterParamCollection:
        """
        Returns task enter parameters collection. If they are not required, must return empty collection
        """
        pass

    @abc.abstractmethod
    def get_headers(self) -> Union[Header, HeaderCollection]:
        """
        Returns all task headers in collection, or just one header
        """
        pass

    def get_schemas(self) -> Union[Schema, SchemaCollection]:
        """
        Returns all task schemas in collection, or just one schema
        """
        pass

    def get_graph_macros(self) -> Union[Macro, MacroCollection]:
        """
        Returns collection of schema macros
        """
        pass

    def get_gis_macros(self) -> Union[Macro, MacroCollection]:
        """
        Returns collection of gis macros
        """
        pass

    def get_weight_function(self) -> str:
        """
        :return: weight calculation function for task
        """
        return '1'

    def get_localization(self) -> 'Localization':
        pass

    def execute(self, enter_params: collections.namedtuple, result_writer: 'ResultWriter', log_writer: 'LogWriter',
                temp_directory: str):
        """
        Payload for task goes here

        :param enter_params:
        :param result_writer:
        :param log_writer:
        :param temp_directory:
        """
        pass


class ResultWriter:
    """
    Writes result row to table(s). This class is not supposed to be instantiated by user.
    """

    def __init__(self, output_file: str, headers: Union[Header, HeaderCollection]):
        """
        Creates ResultWriter instance. For internal usage

        :param output_file: path to file with output files description
        :param headers: Collection of headers or single Header to output
        """
        _Checks.check_arguments(arg_type=str, output_file=output_file)
        if isinstance(headers, HeaderCollection):
            _Checks.check_arguments(headers=headers)
        elif isinstance(headers, Header):
            _Checks.check_arguments(headers=headers)
            headers = [headers]
        else:
            raise TypeError('Headers must be HeaderCollection or single header')

        self._file_paths = {}
        self._headers = {}
        self._file_handlers = {}
        self._field_orders = {}

        self._parse_file_paths(output_file)
        self._add_headers(headers)
        self._set_field_orders()
        self._add_file_handlers()

    def _parse_file_paths(self, path):
        with open(path, 'r', encoding='utf-8') as paths_description:
            lines = [l.strip('\n') for l in paths_description.readlines()]

        last_empty, key, value = True, None, None
        for i in range(0, len(lines)):
            if lines[i] == '':
                last_empty = True
                continue
            elif last_empty:
                key = lines[i]
                last_empty = False
            else:
                value = lines[i]
                self._file_paths[key] = value
                last_empty, key, value = True, None, None

    def _add_headers(self, headers):
        for header in headers:
            _Checks.check_arguments(arg_type=Header, header=header)
            if header.system_name in self._headers:
                raise Exception('Header system name must be unique')
            if header.system_name not in self._file_paths:
                raise Exception('Output file for header not set')
            self._headers[header.system_name] = header

    def _set_field_orders(self):
        for header_sn, header in self._headers.items():
            header_fields = self._field_orders[header_sn] = {}
            fields = list(header.get_fields().values())
            for i in range(0, len(fields)):
                f = fields[i]
                header_fields[f] = i

    def _add_file_handlers(self):
        for sys_name, path in self._file_paths.items():
            fh = open(path, 'w', encoding='utf8', newline='')
            writer = csv.writer(fh, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            self._file_handlers[sys_name] = (fh, writer)

    def _sanitize(self, value):
        if value is not None:
            return str(value).replace('\n', '').replace('\r', '')

    def _detect_header(self, values):
        if len(self._headers) == 1:
            return next(iter(self._headers.values()))

        given_fields = values.keys()
        for sn, field_order in self._field_orders.items():
            saved_fields = field_order.keys()
            if len(given_fields) == len(saved_fields):
                correct = True
                for f in given_fields:
                    if f not in saved_fields:
                        correct = False
                if correct:
                    return self._headers[sn]

    def _header_by_system_names(self, system_names):
        snl = len(system_names)
        for header in self._headers.values():
            if len(header) == snl and set([field.system_name for field in header]) == set(system_names):
                return header

    def _header_by_field_names(self, field_names):
        fnl = len(field_names)
        for header in self._headers.values():
            if len(header) == fnl and set(header.get_fields()) == set(field_names):
                return header

    def write_line(self, values: Dict[Field, Any], header_class: Header = None):
        """
        Writes line of data to specific (or the auto-detected) header

        :param values: flat dictionary of header columns and their values: {header.field: value}
        :param header_class: (optional) [recommended] specify header for line
        """

        header = header_class if header_class else self._detect_header(values)
        if header is None:
            raise Exception('Cannot detect header for values. Check line length and column types')
        file_handler, csv_writer = self._file_handlers[header.system_name]

        if len(header) != len(values):
            raise Exception('Values not fit in header')
        if file_handler.closed:
            raise Exception(f'File is closed: {file_handler.name}')

        value_array = [None] * len(header)
        for (field, value) in values.items():
            order = self._field_orders[header.system_name][field]
            if field.type == ValueType.String:  # remove line breaks, if any
                value = self._sanitize(value)
            value_array[order] = value
        csv_writer.writerow(value_array)

    def write_dataframe(self, dataframe, header_class: Header = None):
        """
        Write pandas Dataframe rows to result table. If no header_class provided,
        columns must be named after field names or field system names

        If header_class IS provided, columns must fit header length (field count)

        :param pandas.Dataframe dataframe:
        :param header_class:
        """
        def flush(handler, df, column_order=None, string_columns=None):
            if string_columns:
                df[string_columns] = df[string_columns].applymap(self._sanitize)  # remove line breaks from strings
            if column_order:
                df = df[column_order]
            df.to_csv(handler, sep=';', header=False, index=False, quoting=csv.QUOTE_MINIMAL,
                      quotechar='"')

        def get_handler(header_cl):
            return self._file_handlers[header_cl.system_name][0]

        def order_and_strings(header_cl, sn=True):
            if sn:
                field_order = [field.system_name for field in header_cl]
                str_cols = [field.system_name for field in header_cl if field.type == ValueType.String]
            else:
                names_and_fields = header_cl.get_fields()
                field_order = list(names_and_fields)
                str_cols = [name for name, field in names_and_fields.items() if field.type == ValueType.String]
            return field_order, str_cols

        column_names = list(dataframe.columns)

        if not header_class:
            header = self._header_by_system_names(column_names)
            if header:
                order, strings = order_and_strings(header)
            else:
                header = self._header_by_field_names(column_names)
                if header:
                    order, strings = order_and_strings(header, sn=False)
                else:
                    raise Exception('Can\'t detect header or values not fit in header')
            flush(get_handler(header), dataframe, order, strings)

        else:
            header = header_class
            file_handler = get_handler(header)

            system_names = [field.system_name for field in header]
            field_names = list(header.get_fields())

            # detect if columns are named after fields or their system_names or columns count just fits header length
            if set(column_names) == set(system_names):
                order, strings = order_and_strings(header)
                flush(file_handler, dataframe, order, strings)
            elif set(column_names) == set(field_names):
                order, strings = order_and_strings(header, sn=False)
                flush(file_handler, dataframe, order, strings)
            else:
                # otherwise, just flush data
                if len(column_names) == len(header):
                    flush(file_handler, dataframe)
                else:
                    raise Exception('Can\'t fit values in header')

    def close(self):
        """
        Closes all output file handlers. For internal usage
        """
        for file_handler, csv_writer in self._file_handlers.values():
            file_handler.close()


class LogWriter:
    """
    Logs user messages to STDOUT or STDERR. This class is not supposed to be instatiated by user.
    """

    def __init__(self):
        """
        Creates LogWriter instance. For internal usage
        """
        pass

    def info(self, message: str, *args):
        """
        Prints formatted message to STDOUT. Formatting is similar to `message.format(*args)`

        :param message: message
        :param args: format arguments
        """
        if len(args) != 0:
            result_message = message.format(*args)
        else:
            result_message = message
        try:
            print(result_message)
        except:
            print(sys.exc_info())
        sys.stdout.flush()

    def error(self, message: str, *args):
        """
        Prints formatted message to STDERR. Formatting is similar to `message.format(*args)`

        :param message: message
        :param str args: format arguments
        """
        if len(args) != 0:
            result_message = message.format(*args)
        else:
            result_message = message
        try:
            print(result_message, file=sys.stderr)
        except:
            print(sys.exc_info())
        sys.stderr.flush()


class RelativeDate:
    """
    Describes relative date using datetime.timedelta for offset
    """
    def __init__(self, reference_point: str, offset: datetime.timedelta):
        """
        :param reference_point: Value from ReferencePoint enum
        :param offset: Use timedelta(0) for current date
        """
        if reference_point not in ReferencePoint.values():
            raise Exception('reference_point must be one of ReferencePoint enum values')
        _Checks.check_arguments(datetime.timedelta, offset=offset)

        self._reference_point = reference_point
        self._offset = offset.total_seconds()

    def to_json(self):
        return {
            'reference_point': self._reference_point,
            'offset': self._offset
        }


class ReferencePoint:
    """
    Starting point options for time offset - from start of the day or current time
    """
    Now = 'Now'
    Today = 'Today'

    @classmethod
    def values(cls) -> Set[str]:
        return {cls.Now, cls.Today}


class LocalizationEntry:
    def __init__(self, scope: str, unique_name: str, translation: str):
        """
        Class for internal use
        """
        self.scope = scope
        self.unique_name = unique_name
        self.translation = translation

    def __repr__(self):
        return f'[{self.scope}][{self.unique_name}] "{self.translation}"'


class LocalizationCulture:
    def __init__(self, name: str, values: Dict[Any, str] = None):
        self.name = name
        self._entries = []
        if values:
            for item in values:
                self.add(item, values[item])

    def add(self, item: Union[Header, Field, EnterParamField, Attribute, Object, Link, Schema, Macro], value: str):
        """
        Add translation for entity or item, for example:\n

        portugal_culture.add(MyHeader.CityField, 'Cidade')\n
        deutsche_culture.add(SomeObject.AgeAttribute, 'Alter')\n
        italian_culture.add(DateEnterparam, 'Data')\n

        :param item: any of type: Header, Field, EnterParamField, Attribute, Object, Link, Schema or Macro.
        :param value: local string
        """
        scope, unique_name = self._scope_and_id(item)
        entry = LocalizationEntry(scope, unique_name, value)
        self._entries.append(entry)

    def manual_add(self, scope: str, unique_name: str, value: str):
        """
        Add translation of something, using unique name (system_name or just name or else). Examples:\n

        greek_culture.manual_add(LocalizationScopes.Macros, 'Search places', 'Αναζήτηση τοποθεσιών')\n
        spanish_culture.manual_add(LocalizationScopes.Task, TaskLocalizationItems.DisplayName, 'Mi tarea personalizada')


        :param scope: Localization entry scope. See available in LocalizationScopes enum
        :param unique_name: system_name for header, field, enterparam or name for link, object, macro, schema, attribute
        :param value: local string
        :return:
        """
        self._entries.append(LocalizationEntry(scope, unique_name, value))

    def to_json(self) -> defaultdict:
        """
        For internal use
        """
        result = defaultdict(dict)
        for entry in self._entries:  # type: LocalizationEntry
            result[entry.scope][entry.unique_name] = entry.translation
        return result

    @staticmethod
    def _scope_and_id(item: Any) -> Tuple[str, str]:
        it = type(item)
        
        if it == Header:
            return LocalizationScopes.Headers, item.system_name
        elif it == Field:
            return LocalizationScopes.Fields, item.system_name
        elif it == EnterParamField:
            return LocalizationScopes.EnterParams, item.system_name
        elif it == Object:
            return LocalizationScopes.Objects, item.name
        elif it == Link:
            return LocalizationScopes.Links, item.name
        elif it == Attribute:
            return LocalizationScopes.Attributes, item.name
        elif it == Schema:
            return LocalizationScopes.Schemas, item.name
        elif it == Macro:
            return LocalizationScopes.Macros, item.name
        else:
            raise TypeError(f'Unsupported type: {it}')


# noinspection PyUnresolvedReferences
class Localization(type):
    """
    Describes how to translate task and entities to another language
    """
    @classmethod
    def __prepare__(mcs, name, bases):
        return collections.OrderedDict()

    def __new__(mcs, name, bases, classdict):
        if bases:
            raise Exception('Localization inheritance is not implemented')

        classdict['__cultures__'] = {key: classdict[key] for key in classdict if key not in
                                     ('__module__', '__qualname__', '__doc__')}

        for c_name in classdict['__cultures__']:
            culture = classdict[c_name]
            if not isinstance(culture, LocalizationCulture):
                raise TypeError(f'Localization cultures must be instances of LocalizationCulture, {type(culture)} given')
            if culture.name is None:
                raise Exception('Culture name is required')
        return type.__new__(mcs, name, bases, classdict)

    def to_json(self) -> Dict[str, Any]:
        return {culture.name: self.__cultures__[name].to_json() for name, culture in self.__cultures__.items()}
