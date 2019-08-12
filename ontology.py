from lighthouse import *
from os.path import join as join_path

NAME = 'System ontology'
ONTOLOGY_ID = 'b811dc34-b029-46fb-a030-8094fc3ce096'


# region Constants
class Constants:
    # arrow for link names, e.g. "Domain → Email"
    RIGHTWARDS_ARROW = '\u2192'
    EN_DASH = '\u2013'
# endregion


# region Helpers
class Utils(Utils):
    """
    extends functionality of lighthouse.Utils
    """

    @classmethod
    def make_schema_name(cls, from_obj_name: str, to_obj_name: str):
        """
        Forms schema name, e.g. Email → Twitter account

        :param from_obj_name: start object
        :param to_obj_name: end object
        :return str:
        """
        return f'{from_obj_name} {Constants.RIGHTWARDS_ARROW} {to_obj_name}'

    # noinspection PyUnresolvedReferences
    @classmethod
    def make_link_name(cls, begin: Object, end: Object):
        if begin.name == end.name:
            return f'{begin.name} {Constants.EN_DASH} {end.name}'
        return f'{begin.name} {Constants.RIGHTWARDS_ARROW} {end.name}'
# endregion


# region Attributes
class AttributesProvider:
    def __init__(self):
        self.__attr_types = {}
        self.System = self.__SystemAttrsProvider()

    # noinspection PyPep8Naming
    class __SystemAttrsProvider:
        @property
        def Emptiness(self):
            return Attributes.str('Emptiness')

        @property
        def UID(self):
            return Attributes.str('UID')

        @property
        def UIDInt(self):
            return Attributes.int('UID integer')

        @property
        def Comment(self):
            return Attributes.str('Comment')

        @property
        def Title(self):
            return Attributes.str('Title')

        @property
        def Description(self):
            return Attributes.str('Description')

        @property
        def Tag(self):
            return Attributes.str('Tag')

        @property
        def Info(self):
            return Attributes.str('Info')

        @property
        def Bio(self):
            return Attributes.str('Bio')

        @property
        def Data(self):
            return Attributes.str('Data')

        @property
        def Text(self):
            return Attributes.str('Text')

        @property
        def RelationType(self):
            return Attributes.str('Relation type')  # universal - how one entity related to another

        @property
        def Datetime(self):
            return Attributes.dt('Datetime')  # system datetime attr

        @property
        def DateString(self):
            return Attributes.str('Date string')

        @property
        def Timestamp(self):
            return Attributes.int('Timestamp')

        @property
        def TimestampStr(self):
            return Attributes.str('Timestamp string')

        @property
        def Document(self):
            return Attributes.str('Document')

        @property
        def Birthday(self):
            return Attributes.dt('Birthday date')

        @property
        def BirthdayStr(self):
            return Attributes.str('Birthday string')

        @property
        def Duration(self):
            return Attributes.int('Duration')

        @property
        def Value(self):
            return Attributes.str('Value')  # system value attr

        @property
        def Count(self):
            return Attributes.int('Count')   # count of something

        @property
        def Number(self):
            return Attributes.int('Number')  # ordinal number of something

        @property
        def DateCreated(self):
            return Attributes.dt('Date created')

        @property
        def Product(self):
            return Attributes.str('Product')

        @property
        def Version(self):
            return Attributes.str('Version')

        @property
        def LastAppearance(self):
            return Attributes.dt('Last appearance')  # common attr

        @property
        def FirstAppearance(self):
            return Attributes.dt('First appearance')  # common attr

        @property
        def OS(self):
            return Attributes.str('OS')  # operating system

        @property
        def TransportLayerProto(self):
            return Attributes.str('Transport layer protocol')  # tcp/udp

        @property
        def AppLayerProto(self):
            return Attributes.str('Application layer protocol')  # http, ftp, etc.

        @property
        def IPAddress(self):
            return Attributes.str('IP address')

        @property
        def IPAndPort(self):
            return Attributes.str('IP and port')

        @property
        def IPInteger(self):
            return Attributes.int('IP integer')

        @property
        def ISP(self):
            return Attributes.str('ISP')  # internet service provider

        @property
        def Port(self):
            return Attributes.int('Port')

        @property
        def MacAddress(self):
            return Attributes.str('MAC address')

        @property
        def ResponseCode(self):
            return Attributes.int('Response code')

        @property
        def Domain(self):
            return Attributes.str('Domain')

        @property
        def Resolved(self):
            return Attributes.dt('Resolve date')  # when domain resolved

        @property
        def ASN(self):
            return Attributes.str('ASN')  # autonomous system number

        @property
        def DomainRegistrant(self):
            return Attributes.str('Domain registrant')

        @property
        def GeoPoint(self):
            return Attributes.str('Geo point')

        @property
        def GeoPolygon(self):
            return Attributes.str('Geo polygon')

        @property
        def GeoLineString(self):
            return Attributes.str('Geo line string')

        @property
        def Latitude(self):
            return Attributes.float('Latitude')

        @property
        def Longitude(self):
            return Attributes.float('Longitude')

        @property
        def Location(self):
            return Attributes.str('Location string')

        @property
        def Region(self):
            return Attributes.str('Region')

        @property
        def Country(self):
            return Attributes.str('Country')

        @property
        def CountryCode(self):
            return Attributes.str('Country code')

        @property
        def Geohash(self):
            return Attributes.str('Geohash')

        @property
        def City(self):
            return Attributes.str('City')

        @property
        def Address(self):
            return Attributes.str('Address')

        @property
        def URL(self):
            return Attributes.str('URL')

        @property
        def Email(self):
            return Attributes.str('Email')

        @property
        def PhoneNumber(self):
            return Attributes.str('Phone number')

        @property
        def IMEI(self):
            return Attributes.str('IMEI')

        @property
        def IMSI(self):
            return Attributes.str('IMSI')

        @property
        def Lac(self):
            return Attributes.int('LAC')

        @property
        def Cell(self):
            return Attributes.int('CELL')

        @property
        def Telco(self):
            return Attributes.str('TELCO')

        @property
        def Azimuth(self):
            return Attributes.float('Azimuth')

        @property
        def Carrier(self):
            return Attributes.str('Carrier')

        @property
        def Credentials(self):
            return Attributes.str('Credentials')  # surname, name, middlename

        @property
        def Name(self):
            return Attributes.str('Name')

        @property
        def Surname(self):
            return Attributes.str('Surname')

        @property
        def MiddleName(self):
            return Attributes.str('Middle name')

        @property
        def Login(self):
            return Attributes.str('Login')

        @property
        def Nickname(self):
            return Attributes.str('Nickname')

        @property
        def Sex(self):
            return Attributes.str('Sex')

        @property
        def University(self):
            return Attributes.str('University')

        @property
        def School(self):
            return Attributes.str('School')

        @property
        def Work(self):
            return Attributes.str('Work')

        @property
        def Occupation(self):
            return Attributes.str('Occupation')

        @property
        def Role(self):
            return Attributes.str('Role')

        @property
        def MaritalStatus(self):
            return Attributes.str('Marital status')

        @property
        def OrgName(self):
            return Attributes.str('Organisation name')

        @property
        def PostsCount(self):
            return Attributes.int('Posts count')

        @property
        def FollowersCount(self):
            return Attributes.int('Followers count')

        @property
        def FollowingCount(self):
            return Attributes.int('Following count')

        @property
        def VIN(self):
            return Attributes.str('VIN')

        @property
        def LicensePlate(self):
            return Attributes.str('License plate number')

        @property
        def Manufacturer(self):
            return Attributes.str('Manufacturer')

        @property
        def Hash(self):
            return Attributes.str('Hash')

        @property
        def HashDigest(self):
            return Attributes.int('Hash integer')

        @property
        def HashAlgo(self):
            return Attributes.str('Hashing algorithm')

        @property
        def DateAccessed(self):
            return Attributes.dt('Date accessed')

        @property
        def DateModified(self):
            return Attributes.dt('Date modified')

        @property
        def Filename(self):
            return Attributes.str('Filename')



        @property
        def FileType(self):
            return Attributes.str('File type')

        @property
        def FileSize(self):
            return Attributes.int('File size')

        @property
        def ThreatName(self):
            return Attributes.str('Threat name')

        @property
        def FacebookID(self):
            return Attributes.str('Facebook id')

        @property
        def ICQID(self):
            return Attributes.str('Icq id')

        @property
        def TwitterID(self):
            return Attributes.str('Twitter id')

        @property
        def FlickrId(self):
            return Attributes.str('Flickr id')

        @property
        def TelegramId(self):
            return Attributes.str('Telegram id')

        @property
        def LinkedinId(self):
            return Attributes.str('Linkedin id')

        @property
        def CurrentWork(self):
            return Attributes.str('Current work')

        @property
        def OrganisationSite(self):
            return Attributes.str('Organisation site')

        @property
        def AcademicDegree(self):
            return Attributes.str('Academic degree')

        @property
        def EntranceYear(self):
            return Attributes.int('Entrance year')

        @property
        def GraduationYear(self):
            return Attributes.int('Graduation year')

        @property
        def WorkStartDate(self):
            return Attributes.dt('Work start date')

        @property
        def WorkEndDate(self):
            return Attributes.dt('Work end date')

        @property
        def Brand(self):
            return Attributes.str('Brand')

        @property
        def Model(self):
            return Attributes.str('Model')

        @property
        def BodyStyle(self):
            return Attributes.str('Body style')

        @property
        def EngineType(self):
            return Attributes.str('Engine type')

        @property
        def FuelType(self):
            return Attributes.str('Fuel type')

        @property
        def Driveline(self):
            return Attributes.str('Driveline')

        @property
        def Transmission(self):
            return Attributes.str('Transmission')

        @property
        def ProductionYear(self):
            return Attributes.int('Production year')

        @property
        def EnginePower(self):
            return Attributes.int('Engine power')

        @property
        def RegistrationId(self):
            return Attributes.str('Registration id')

    @property
    def Netblock(self):
        return self.str('Netblock')

    @property
    def FilePath(self):
        return Attributes.str('File path')



    # region Internal methods
    def generate(self, name, vtype):
        if not name:
            raise Exception('Attribute name can\'t be empty')

        if name in self.__attr_types and vtype != self.__attr_types[name]:
                raise Exception(f'Attribute {name} redeclared with different type')
        else:
            self.__attr_types[name] = vtype
        return Attribute(name, vtype)  # must be always new instance

    def str(self, name):
        return self.generate(name, ValueType.String)

    def int(self, name):
        return self.generate(name, ValueType.Integer)

    def float(self, name):
        return self.generate(name, ValueType.Float)

    def bool(self, name):
        return self.generate(name, ValueType.Boolean)

    def dt(self, name):
        return self.generate(name, ValueType.Datetime)
    # endregion


# usage:
# Attributes.System.Port
# Attributes.Comment
Attributes = AttributesProvider()
# endregion


# region Objects
# region System objects
class Entity(metaclass=Object):
    Value = Attributes.System.Value

    IdentAttrs = CaptionAttrs = [Value]


class Email(metaclass=Object):
    Email = Attributes.System.Email

    IdentAttrs = CaptionAttrs = [Email]


class Phone(metaclass=Object):
    Number = Attributes.System.PhoneNumber
    IMEI = Attributes.System.IMEI
    IMSI = Attributes.System.IMSI

    IdentAttrs = CaptionAttrs = [Number]


class Address(metaclass=Object):
    Address = Attributes.System.Address
    GeoPoint = Attributes.System.GeoPoint

    IdentAttrs = [Address, GeoPoint]
    CaptionAttrs = [Address]


class Location(metaclass=Object):
    Name = Attributes.System.Location
    City = Attributes.System.City
    Country = Attributes.System.Country
    CountryCode = Attributes.System.CountryCode
    Address = Attributes.System.Address
    Latitude = Attributes.System.Latitude
    Longitude = Attributes.System.Longitude
    GeoPoint = Attributes.System.GeoPoint
    Geohash = Attributes.System.Geohash

    IdentAttrs = [Name, City, Country, Latitude, Longitude, Geohash, GeoPoint]
    CaptionAttrs = [Name, Address]


class BaseStation(metaclass=Object):
    name = 'Base station'

    Lac = Attributes.System.Lac
    Cell = Attributes.System.Cell
    Telco = Attributes.System.Telco
    Address = Attributes.System.Address
    Azimuth = Attributes.System.Azimuth
    GeoPoint = Attributes.System.GeoPoint
    GeoPolygon = Attributes.System.GeoPolygon

    IdentAttrs = [Lac, Cell]
    CaptionAttrs = IdentAttrs + [Telco, Address, Azimuth]


class PhoneNumber(metaclass=Object):
    name = 'Phone number'

    Number = Attributes.System.PhoneNumber

    IdentAttrs = CaptionAttrs = [Number]


class IMEI(metaclass=Object):
    IMEI = Attributes.System.IMEI

    IdentAttrs = CaptionAttrs = [IMEI]


class IMSI(metaclass=Object):
    IMSI = Attributes.System.IMSI

    IdentAttrs = CaptionAttrs = [IMSI]


class CallEvent(metaclass=Object):
    name = 'Call event'

    PhoneNumber = Attributes.System.PhoneNumber
    DateTime = Attributes.System.Datetime
    Duration = Attributes.System.Duration
    Lac = Attributes.System.Lac
    Cell = Attributes.System.Cell
    Telco = Attributes.System.Telco
    Address = Attributes.System.Address
    GeoPoint = Attributes.System.GeoPoint

    IdentAttrs = [PhoneNumber, DateTime, Duration, Lac, Cell]
    CaptionAttrs = IdentAttrs + [Telco]


class Webcam(metaclass=Object):
    IPAddress = Attributes.System.IPAddress
    Port = Attributes.System.Port
    Address = Attributes.System.Address
    GeoPoint = Attributes.System.GeoPoint

    IdentAttrs = [IPAddress, Port]
    CaptionAttrs = IdentAttrs + [Address]


class Domain(metaclass=Object):
    Domain = Attributes.System.Domain
    # IP = Attributes.System.IPAddress

    IdentAttrs = CaptionAttrs = [Domain]


class Car(metaclass=Object):
    Plate = Attributes.System.LicensePlate
    VIN = Attributes.System.VIN
    RegistrationId = Attributes.System.RegistrationId
    Manufacturer = Attributes.System.Manufacturer
    ProductionYear = Attributes.System.ProductionYear
    Brand = Attributes.System.Brand
    Model = Attributes.System.Model
    BodyStyle = Attributes.System.BodyStyle
    EngineType = Attributes.System.EngineType
    EnginePower = Attributes.System.EnginePower
    FuelType = Attributes.System.FuelType
    Driveline = Attributes.System.Driveline
    Transmission = Attributes.System.Transmission

    IdentAttrs = [VIN, Plate, RegistrationId]
    CaptionAttrs = [VIN, Plate]


class CarRecord(metaclass=Object):
    name = 'Car record'

    Plate = Attributes.System.LicensePlate
    DateTime = Attributes.System.Datetime
    GeoPoint = Attributes.System.GeoPoint

    IdentAttrs = CaptionAttrs = [Plate]


class Point(metaclass=Object):
    Value = Attributes.System.Value
    Address = Attributes.System.Address
    Point = Attributes.System.GeoPoint

    IdentAttrs = [Value, Point]
    CaptionAttrs = [Value]


class IP(metaclass=Object):
    name = 'IP'

    IP = Attributes.System.IPAddress

    IdentAttrs = CaptionAttrs = [IP]


class NetworkInterface(metaclass=Object):
    name = 'Network interface'

    IP = Attributes.System.IPAddress
    Mac = Attributes.System.MacAddress

    IdentAttrs = CaptionAttrs = [IP, Mac]


class URL(metaclass=Object):
    URL = Attributes.System.URL

    IdentAttrs = CaptionAttrs = [URL]


class Hash(metaclass=Object):
    Hash = Attributes.System.Hash
    Algo = Attributes.System.HashAlgo

    IdentAttrs = CaptionAttrs = [Hash, Algo]


class AutonomousSystem(metaclass=Object):
    name = 'Autonomous system'
    ASN = Attributes.System.ASN

    IdentAttrs = CaptionAttrs = [ASN]


class Port(metaclass=Object):
    Port = Attributes.System.Port

    IdentAttrs = CaptionAttrs = [Port]


class APT(metaclass=Object):  # Advanced persistent threat
    ThreatName = Attributes.System.ThreatName

    IdentAttrs = CaptionAttrs = [ThreatName]


class Organisation(metaclass=Object):
    OrgName = Attributes.System.OrgName

    IdentAttrs = CaptionAttrs = [OrgName]


class City(metaclass=Object):
    City = Attributes.System.City
    Country = Attributes.System.Country

    IdentAttrs = [City, Country]
    CaptionAttrs = [City]


class School(metaclass=Object):
    School = Attributes.System.School

    IdentAttrs = [School]
    CaptionAttrs = [School]


class Country(metaclass=Object):
    Country = Attributes.System.Country

    IdentAttrs = CaptionAttrs = [Country]


class University(metaclass=Object):
    University = Attributes.System.University

    IdentAttrs = CaptionAttrs = [University]


class Work(metaclass=Object):
    Work = Attributes.System.Work
    Location = Attributes.System.Location
    GeoPoint = Attributes.System.GeoPoint

    IdentAttrs = CaptionAttrs = [Work]


class Person(metaclass=Object):
    Name = Attributes.System.Name
    Surname = Attributes.System.Surname
    Middlename = Attributes.System.MiddleName
    Credentials = Attributes.System.Credentials
    Document = Attributes.System.Document
    Sex = Attributes.System.Sex
    Birthday = Attributes.System.Birthday

    IdentAttrs = [Name, Surname, Middlename, Credentials, Birthday]
    CaptionAttrs = [Name, Surname, Middlename, Credentials]


class SkypeAccount(metaclass=Object):
    name = 'Skype account'

    Login = Attributes.System.Login
    Fullname = Attributes.System.Name

    IdentAttrs = [Login]
    CaptionAttrs = [Login, Fullname]


class FacebookAccount(metaclass=Object):
    name = 'Facebook account'

    Credentials = Attributes.System.Credentials
    UID = Attributes.System.FacebookID
    Nickname = Attributes.System.Nickname
    URL = Attributes.System.URL
    Country = Attributes.System.Country
    City = Attributes.System.City
    Phone = Attributes.System.PhoneNumber
    BirthdayStr = Attributes.System.BirthdayStr
    Sex = Attributes.System.Sex
    MaritalStatus = Attributes.System.MaritalStatus
    LastAppearance = Attributes.System.LastAppearance
    School = Attributes.System.School
    University = Attributes.System.University
    Work = Attributes.System.Work
    Occupation = Attributes.System.Occupation
    GeoPoint = Attributes.System.GeoPoint

    IdentAttrs = [UID]
    CaptionAttrs = [Credentials, Nickname, URL]


class TelegramAccount(metaclass=Object):
    name = 'Telegram account'

    TelegramId = Attributes.System.TelegramId
    Firstname = Attributes.System.Name
    Lastname = Attributes.System.Surname
    PhoneNumber = Attributes.System.PhoneNumber
    Nickname = Attributes.System.Nickname
    Bio = Attributes.System.Bio
    LastAppearance = Attributes.System.LastAppearance

    IdentAttrs = [PhoneNumber]
    CaptionAttrs = [Nickname, Firstname, Lastname]


class WhatsappAccount(metaclass=Object):
    name = 'Whatsapp account'

    PhoneNumber = Attributes.System.PhoneNumber
    LastAppearance = Attributes.System.LastAppearance

    IdentAttrs = CaptionAttrs = [PhoneNumber]


class LinkedinAccount(metaclass=Object):
    name = 'Linkedin account'

    LinkedinId = Attributes.System.LinkedinId
    Credentials = Attributes.System.Credentials
    Organization = Attributes.System.OrgName
    OrganisationSite = Attributes.System.OrganisationSite
    Occupation = Attributes.System.Occupation
    Location = Attributes.System.Location
    Geopoint = Attributes.System.GeoPoint
    URL = Attributes.System.URL

    IdentAttrs = [URL]
    CaptionAttrs = [Credentials, Organization, URL]


class IcqAccount(metaclass=Object):
    name = 'Icq account'

    Credentials = Attributes.System.Credentials
    UID = Attributes.System.ICQID
    URL = Attributes.System.URL
    Birthday = Attributes.System.Birthday

    IdentAttrs = [UID]
    CaptionAttrs = [Credentials, URL]


class GooglePlusAccount(metaclass=Object):
    name = 'Googleplus account'

    Credentials = Attributes.System.Credentials
    Nickname = Attributes.System.Nickname
    URL = Attributes.System.URL

    IdentAttrs = [URL]
    CaptionAttrs = [Credentials, URL]


class FlickrAccount(metaclass=Object):
    name = 'Flickr account'

    FlickrId = Attributes.System.FlickrId
    URL = Attributes.System.URL

    DateCreated = Attributes.System.DateCreated
    GeoPoint = Attributes.System.GeoPoint

    Bio = Attributes.System.Bio
    Nickname = Attributes.System.Nickname
    Credentials = Attributes.System.Credentials

    PostsCount = Attributes.System.PostsCount
    FollowersCount = Attributes.System.FollowersCount
    FollowingCount = Attributes.System.FollowingCount

    IdentAttrs = [FlickrId]
    CaptionAttrs = [Nickname, Credentials, URL]


class FoursquareAccount(metaclass=Object):
    name = 'Foursquare account'

    Credentials = Attributes.System.Credentials
    URL = Attributes.System.URL
    Location = Attributes.System.Location
    Sex = Attributes.System.Sex

    IdentAttrs = [URL]
    CaptionAttrs = [Credentials, Location, Sex, URL]


class GithubAccount(metaclass=Object):
    name = 'Github account'

    Credentials = Attributes.System.Credentials
    Nickname = Attributes.System.Nickname
    URL = Attributes.System.URL

    IdentAttrs = [URL]
    CaptionAttrs = [Nickname, URL]


class TwitterAccount(metaclass=Object):
    name = 'Twitter account'

    Credentials = Attributes.System.Credentials
    Location = Attributes.System.Location
    Created = Attributes.System.DateCreated
    UID = Attributes.System.TwitterID
    URL = Attributes.System.URL
    Bio = Attributes.System.Bio
    GeoPoint = Attributes.System.GeoPoint

    IdentAttrs = [UID]
    CaptionAttrs = [Credentials, URL]


class MyspaceAccount(metaclass=Object):
    name = 'Myspace account'

    Credentials = Attributes.System.Credentials
    Nickname = Attributes.System.Nickname
    GeoPoint = Attributes.System.GeoPoint
    URL = Attributes.System.URL

    IdentAttrs = [URL]
    CaptionAttrs = [Credentials, URL]


class PhoneBook(metaclass=Object):
    name = 'Phone book'

    PhoneNumber = Attributes.System.PhoneNumber
    Credentials = Attributes.System.Credentials
    Firstname = Attributes.System.Name
    Lastname = Attributes.System.Surname
    Country = Attributes.System.Country
    City = Attributes.System.City
    Carrier = Attributes.System.Carrier

    IdentAttrs = [PhoneNumber, Credentials]
    CaptionAttrs = [PhoneNumber, Credentials]


class Netblock(metaclass=Object):
    Netblock = Attributes.Netblock

    IdentAttrs = CaptionAttrs = [Netblock]
    Image = Utils.base64string(join_path('static/icons/common', 'netblock.png'))

# endregion
# endregion


# region Links
# region System links
class Call(metaclass=Link):
    name = 'Call'

    CallTime = Attributes.System.Datetime
    Duration = Attributes.System.Duration

    Begin = Phone
    End = Phone


class IPToDomain(metaclass=Link):
    name = Utils.make_link_name(IP, Domain)

    Resolved = Attributes.System.Resolved

    Begin = IP
    End = Domain


class IPToEmail(metaclass=Link):
    name = Utils.make_link_name(IP, Email)

    DateTime = Attributes.System.Datetime

    Begin = IP
    End = Email


class IPToPerson(metaclass=Link):
    name = Utils.make_link_name(IP, Person)

    DateTime = Attributes.System.Datetime

    Begin = IP
    End = Person


class IPToAPT(metaclass=Link):
    name = Utils.make_link_name(IP, APT)

    DateTime = Attributes.System.Datetime

    Begin = IP
    End = APT


class IPToAutonomousSystem(metaclass=Link):
    name = Utils.make_link_name(IP, AutonomousSystem)

    Value = Attributes.System.Value

    Begin = IP
    End = AutonomousSystem


class IPToCity(metaclass=Link):
    name = Utils.make_link_name(IP, City)

    Value = Attributes.System.Value

    Begin = IP
    End = City


class IPToCountry(metaclass=Link):
    name = Utils.make_link_name(IP, Country)

    Value = Attributes.System.Value

    Begin = IP
    End = Country


class IPToEntity(metaclass=Link):
    name = Utils.make_link_name(IP, Entity)

    Value = Attributes.System.Value

    Begin = IP
    End = Entity


class IPToIP(metaclass=Link):
    name = Utils.make_link_name(IP, IP)

    Value = Attributes.System.Value

    Begin = IP
    End = IP


class IPToLocation(metaclass=Link):
    name = Utils.make_link_name(IP, Location)

    DateTime = Attributes.System.Datetime

    Begin = IP
    End = Location


class IPToOrganisation(metaclass=Link):
    name = Utils.make_link_name(IP, Organisation)

    Value = Attributes.System.Value

    Begin = IP
    End = Organisation


class IPToPhone(metaclass=Link):
    name = Utils.make_link_name(IP, Phone)

    Value = Attributes.System.Value

    Begin = IP
    End = Phone


class IPToSchool(metaclass=Link):
    name = Utils.make_link_name(IP, School)

    Value = Attributes.System.Value

    Begin = IP
    End = School


class IPToTelegramAccount(metaclass=Link):
    name = Utils.make_link_name(IP, TelegramAccount)

    Value = Attributes.System.Value

    Begin = IP
    End = TelegramAccount


class IPToURL(metaclass=Link):
    name = Utils.make_link_name(IP, URL)

    Value = Attributes.System.Value

    Begin = IP
    End = URL


class IPToUniversity(metaclass=Link):
    name = Utils.make_link_name(IP, University)

    Value = Attributes.System.Value

    Begin = IP
    End = University


class DomainToDomain(metaclass=Link):
    name = Utils.make_link_name(Domain, Domain)

    RelationType = Attributes.System.RelationType

    Begin = Domain
    End = Domain


class EntityToEntity(metaclass=Link):
    name = Utils.make_link_name(Entity, Entity)

    Value = Attributes.System.Value

    Begin = Entity
    End = Entity


class PortToIP(metaclass=Link):
    name = Utils.make_link_name(Port, IP)

    Transport = Attributes.System.TransportLayerProto
    Product = Attributes.System.Product

    Begin = Port
    End = IP


class CallEventToAPT(metaclass=Link):
    name = Utils.make_link_name(CallEvent, APT)

    DateTime = Attributes.System.Datetime

    Begin = CallEvent
    End = APT


class CallEventToAddress(metaclass=Link):
    name = Utils.make_link_name(CallEvent, Address)

    DateTime = Attributes.System.Datetime

    Begin = CallEvent
    End = Address


class CallEventToBaseStation(metaclass=Link):
    name = Utils.make_link_name(CallEvent, BaseStation)

    DateTime = Attributes.System.Datetime

    Begin = CallEvent
    End = BaseStation


class CallEventToEmail(metaclass=Link):
    name = Utils.make_link_name(CallEvent, Email)

    DateTime = Attributes.System.Datetime

    Begin = CallEvent
    End = Email


class CallEventToEntity(metaclass=Link):
    name = Utils.make_link_name(CallEvent, Entity)

    DateTime = Attributes.System.Datetime

    Begin = CallEvent
    End = Entity


class CallEventToLocation(metaclass=Link):
    name = Utils.make_link_name(CallEvent, Location)

    DateTime = Attributes.System.Datetime

    Begin = CallEvent
    End = Location


class CallEventToPerson(metaclass=Link):
    name = Utils.make_link_name(CallEvent, Person)

    DateTime = Attributes.System.Datetime

    Begin = CallEvent
    End = Person


class CallEventToPhone(metaclass=Link):
    name = Utils.make_link_name(CallEvent, Phone)

    DateTime = Attributes.System.Datetime

    Begin = CallEvent
    End = Phone


class CallEventToPhoneNumber(metaclass=Link):
    name = Utils.make_link_name(CallEvent, PhoneNumber)

    DateTime = Attributes.System.Datetime

    Begin = CallEvent
    End = PhoneNumber


class PhoneToIMEI(metaclass=Link):
    name = Utils.make_link_name(Phone, IMEI)

    DateTime = Attributes.System.Datetime

    Begin = Phone
    End = IMEI


class PhoneToIMSI(metaclass=Link):
    name = Utils.make_link_name(Phone, IMSI)

    DateTime = Attributes.System.Datetime

    Begin = Phone
    End = IMSI


class PhoneToBaseStation(metaclass=Link):
    name = Utils.make_link_name(Phone, BaseStation)

    DateTime = Attributes.System.Datetime

    Begin = Phone
    End = BaseStation


class PhoneToPerson(metaclass=Link):
    name = Utils.make_link_name(Phone, Person)

    DateTime = Attributes.System.Datetime

    Begin = Phone
    End = Person


class PhoneNumberToIMEI(metaclass=Link):
    name = Utils.make_link_name(PhoneNumber, IMEI)

    DateTime = Attributes.System.Datetime

    Begin = PhoneNumber
    End = IMEI


class PhoneNumberToIMSI(metaclass=Link):
    name = Utils.make_link_name(PhoneNumber, IMSI)

    DateTime = Attributes.System.Datetime

    Begin = PhoneNumber
    End = IMSI


class PhoneNumberToPerson(metaclass=Link):
    name = Utils.make_link_name(PhoneNumber, Person)

    DateTime = Attributes.System.Datetime

    Begin = PhoneNumber
    End = Person


class HashToEmail(metaclass=Link):
    name = Utils.make_link_name(Hash, Email)

    Value = Attributes.System.Value

    Begin = Hash
    End = Email


class HashToIP(metaclass=Link):
    name = Utils.make_link_name(Hash, IP)

    DateTime = Attributes.System.Datetime

    Begin = Hash
    End = IP


class EmailToPerson(metaclass=Link):
    name = Utils.make_link_name(Email, Person)

    DateTime = Attributes.System.Datetime

    Begin = Email
    End = Person


class EmailToDomain(metaclass=Link):
    name = Utils.make_link_name(Email, Domain)

    DateTime = Attributes.System.Datetime

    Begin = Email
    End = Domain


class EmailToPhoneLink(metaclass=Link):
    name = Utils.make_link_name(Email, Phone)

    DateTime = Attributes.System.Datetime

    Begin = Email
    End = Phone


class EmailToSkypeAccount(metaclass=Link):
    name = Utils.make_link_name(Email, SkypeAccount)

    Value = Attributes.System.Value

    Begin = Email
    End = SkypeAccount


class EmailToFacebookAccount(metaclass=Link):
    name = Utils.make_link_name(Email, FacebookAccount)

    Value = Attributes.System.Value

    Begin = Email
    End = FacebookAccount


class EmailToTelegramAccount(metaclass=Link):
    name = Utils.make_link_name(Email, TelegramAccount)

    Value = Attributes.System.Value

    Begin = Email
    End = TelegramAccount


class EmailToWhatsappAccount(metaclass=Link):
    name = Utils.make_link_name(Email, WhatsappAccount)

    Value = Attributes.System.Value

    Begin = Email
    End = WhatsappAccount


class EmailToLinkedinAccount(metaclass=Link):
    name = Utils.make_link_name(Email, LinkedinAccount)

    Value = Attributes.System.Value

    Begin = Email
    End = LinkedinAccount


class EmailToIcqAccount(metaclass=Link):
    name = Utils.make_link_name(Email, IcqAccount)

    Value = Attributes.System.Value

    Begin = Email
    End = IcqAccount


class EmailToGooglePlusAccount(metaclass=Link):
    name = Utils.make_link_name(Email, GooglePlusAccount)

    Value = Attributes.System.Value

    Begin = Email
    End = GooglePlusAccount


class EmailToFlickrAccount(metaclass=Link):
    name = Utils.make_link_name(Email, FlickrAccount)

    Value = Attributes.System.Value

    Begin = Email
    End = FlickrAccount


class EmailToFoursquareAccount(metaclass=Link):
    name = Utils.make_link_name(Email, FoursquareAccount)

    Value = Attributes.System.Value

    Begin = Email
    End = FoursquareAccount


class EmailToGithubAccount(metaclass=Link):
    name = Utils.make_link_name(Email, GithubAccount)

    Value = Attributes.System.Value

    Begin = Email
    End = GithubAccount


class EmailToTwitterAccount(metaclass=Link):
    name = Utils.make_link_name(Email, TwitterAccount)

    Value = Attributes.System.Value

    Begin = Email
    End = TwitterAccount


class EmailToMyspaceAccount(metaclass=Link):
    name = Utils.make_link_name(Email, MyspaceAccount)

    Value = Attributes.System.Value

    Begin = Email
    End = MyspaceAccount


class EmailToAPT(metaclass=Link):
    name = Utils.make_link_name(Email, APT)

    Value = Attributes.System.Value

    Begin = Email
    End = APT


class EmailToEmail(metaclass=Link):
    name = Utils.make_link_name(Email, Email)

    Value = Attributes.System.Value

    Begin = Email
    End = Email


class EmailToEntity(metaclass=Link):
    name = Utils.make_link_name(Email, Entity)

    Value = Attributes.System.Value

    Begin = Email
    End = Entity


class EmailToOrganisation(metaclass=Link):
    name = Utils.make_link_name(Email, Organisation)

    Value = Attributes.System.Value

    Begin = Email
    End = Organisation


class EmailToSchool(metaclass=Link):
    name = Utils.make_link_name(Email, School)

    Value = Attributes.System.Value

    Begin = Email
    End = School


class EmailToUniversity(metaclass=Link):
    name = Utils.make_link_name(Email, University)

    Value = Attributes.System.Value

    Begin = Email
    End = University


class EmailToWork(metaclass=Link):
    name = Utils.make_link_name(Email, Work)

    Value = Attributes.System.Value

    Begin = Email
    End = Work


class CityToCountry(metaclass=Link):
    Begin = City
    End = Country


class PhoneToSkypeAccount(metaclass=Link):
    name = Utils.make_link_name(Phone, SkypeAccount)

    Value = Attributes.System.Value

    Begin = Phone
    End = SkypeAccount


class PhoneToFacebookAccount(metaclass=Link):
    name = Utils.make_link_name(Phone, FacebookAccount)

    Value = Attributes.System.Value

    Begin = Phone
    End = FacebookAccount


class PhoneToTelegramAccount(metaclass=Link):
    name = Utils.make_link_name(Phone, TelegramAccount)

    Value = Attributes.System.Value

    Begin = Phone
    End = TelegramAccount


class PhoneToWhatsappAccount(metaclass=Link):
    name = Utils.make_link_name(Phone, WhatsappAccount)

    Value = Attributes.System.Value

    Begin = Phone
    End = WhatsappAccount


class PhoneToLinkedinAccount(metaclass=Link):
    name = Utils.make_link_name(Phone, LinkedinAccount)

    Value = Attributes.System.Value

    Begin = Phone
    End = LinkedinAccount


class PhoneToIcqAccount(metaclass=Link):
    name = Utils.make_link_name(Phone, IcqAccount)

    Value = Attributes.System.Value

    Begin = Phone
    End = IcqAccount


class PhoneToGooglePlusAccount(metaclass=Link):
    name = Utils.make_link_name(Phone, GooglePlusAccount)

    Value = Attributes.System.Value

    Begin = Phone
    End = GooglePlusAccount


class PhoneToFlickrAccount(metaclass=Link):
    name = Utils.make_link_name(Phone, FlickrAccount)

    Value = Attributes.System.Value

    Begin = Phone
    End = FlickrAccount


class PhoneToFoursquareAccount(metaclass=Link):
    name = Utils.make_link_name(Phone, FoursquareAccount)

    Value = Attributes.System.Value

    Begin = Phone
    End = FoursquareAccount


class PhoneToGithubAccount(metaclass=Link):
    name = Utils.make_link_name(Phone, GithubAccount)

    Value = Attributes.System.Value

    Begin = Phone
    End = GithubAccount


class PhoneToTwitterAccount(metaclass=Link):
    name = Utils.make_link_name(Phone, TwitterAccount)

    Value = Attributes.System.Value

    Begin = Phone
    End = TwitterAccount


class PhoneToMyspaceAccount(metaclass=Link):
    name = Utils.make_link_name(Phone, MyspaceAccount)

    Value = Attributes.System.Value

    Begin = Phone
    End = MyspaceAccount


class SkypeAccountToPerson(metaclass=Link):
    name = Utils.make_link_name(SkypeAccount, Person)

    Value = Attributes.System.Value

    Begin = SkypeAccount
    End = Person


class FacebookAccountToPerson(metaclass=Link):
    name = Utils.make_link_name(FacebookAccount, Person)

    Value = Attributes.System.Value

    Begin = FacebookAccount
    End = Person


class FacebookAccountToFacebookAccount(metaclass=Link):
    name = Utils.make_link_name(FacebookAccount, FacebookAccount)

    Value = Attributes.System.Value

    Begin = FacebookAccount
    End = FacebookAccount


class FacebookAccountToCountry(metaclass=Link):
    name = Utils.make_link_name(FacebookAccount, Country)

    Value = Attributes.System.Value

    Begin = FacebookAccount
    End = Country


class FacebookAccountToOrganisation(metaclass=Link):
    name = Utils.make_link_name(FacebookAccount, Organisation)

    Value = Attributes.System.Value

    Begin = FacebookAccount
    End = Organisation


class FacebookAccountToWork(metaclass=Link):
    name = Utils.make_link_name(FacebookAccount, Work)

    Value = Attributes.System.Value

    Begin = FacebookAccount
    End = Work


class FacebookAccountToSchool(metaclass=Link):
    name = Utils.make_link_name(FacebookAccount, School)

    Value = Attributes.System.Value

    Begin = FacebookAccount
    End = School


class FacebookAccountToUniversity(metaclass=Link):
    name = Utils.make_link_name(FacebookAccount, University)

    Value = Attributes.System.Value

    Begin = FacebookAccount
    End = University


class TelegramAccountToPerson(metaclass=Link):
    name = Utils.make_link_name(TelegramAccount, Person)

    Value = Attributes.System.Value

    Begin = TelegramAccount
    End = Person


class WhatsappAccountToPerson(metaclass=Link):
    name = Utils.make_link_name(WhatsappAccount, Person)

    Value = Attributes.System.Value

    Begin = WhatsappAccount
    End = Person


class LinkedinAccountToPerson(metaclass=Link):
    name = Utils.make_link_name(LinkedinAccount, Person)

    Value = Attributes.System.Value

    Begin = LinkedinAccount
    End = Person


class IcqAccountToPerson(metaclass=Link):
    name = Utils.make_link_name(IcqAccount, Person)

    Value = Attributes.System.Value

    Begin = IcqAccount
    End = Person


class GooglePlusAccountToPerson(metaclass=Link):
    name = Utils.make_link_name(GooglePlusAccount, Person)

    Value = Attributes.System.Value

    Begin = GooglePlusAccount
    End = Person


class FlickrAccountToPerson(metaclass=Link):
    name = Utils.make_link_name(FlickrAccount, Person)

    Value = Attributes.System.Value

    Begin = FlickrAccount
    End = Person


class FoursquareAccountToPerson(metaclass=Link):
    name = Utils.make_link_name(FoursquareAccount, Person)

    Value = Attributes.System.Value

    Begin = FoursquareAccount
    End = Person


class GithubAccountToPerson(metaclass=Link):
    name = Utils.make_link_name(GithubAccount, Person)

    Value = Attributes.System.Value

    Begin = GithubAccount
    End = Person


class TwitterAccountToPerson(metaclass=Link):
    name = Utils.make_link_name(TwitterAccount, Person)

    Value = Attributes.System.Value

    Begin = TwitterAccount
    End = Person


class MyspaceAccountToPerson(metaclass=Link):
    name = Utils.make_link_name(MyspaceAccount, Person)

    Value = Attributes.System.Value

    Begin = MyspaceAccount
    End = Person


class UniversityToLocation(metaclass=Link):
    name = Utils.make_link_name(University, Location)

    Value = Attributes.System.Value

    Begin = University
    End = Location


class WorkToLocation(metaclass=Link):
    name = Utils.make_link_name(Work, Location)

    Value = Attributes.System.Value

    Begin = Work
    End = Location


class PersonToLocation(metaclass=Link):
    name = Utils.make_link_name(Person, Location)

    Value = Attributes.System.Value

    Begin = Person
    End = Location


class PersonToCountry(metaclass=Link):
    name = Utils.make_link_name(Person, Country)

    Value = Attributes.System.Value

    Begin = Person
    End = Country


class PersonToCity(metaclass=Link):
    name = Utils.make_link_name(Person, City)

    Value = Attributes.System.Value

    Begin = Person
    End = City


class SkypeAccountToLocation(metaclass=Link):
    name = Utils.make_link_name(SkypeAccount, Location)

    Value = Attributes.System.Value

    Begin = SkypeAccount
    End = Location


class FacebookAccountToLocation(metaclass=Link):
    name = Utils.make_link_name(FacebookAccount, Location)

    Value = Attributes.System.Value

    Begin = FacebookAccount
    End = Location


class TelegramAccountToLocation(metaclass=Link):
    name = Utils.make_link_name(TelegramAccount, Location)

    Value = Attributes.System.Value

    Begin = TelegramAccount
    End = Location


class WhatsappAccountToLocation(metaclass=Link):
    name = Utils.make_link_name(WhatsappAccount, Location)

    Value = Attributes.System.Value

    Begin = WhatsappAccount
    End = Location


class LinkedinAccountToLocation(metaclass=Link):
    name = Utils.make_link_name(LinkedinAccount, Location)

    Value = Attributes.System.Value

    Begin = LinkedinAccount
    End = Location


class IcqAccountToLocation(metaclass=Link):
    name = Utils.make_link_name(IcqAccount, Location)

    Value = Attributes.System.Value

    Begin = IcqAccount
    End = Location


class GooglePlusAccountToLocation(metaclass=Link):
    name = Utils.make_link_name(GooglePlusAccount, Location)

    Value = Attributes.System.Value

    Begin = GooglePlusAccount
    End = Location


class FlickrAccountToLocation(metaclass=Link):
    name = Utils.make_link_name(FlickrAccount, Location)

    Value = Attributes.System.Value

    Begin = FlickrAccount
    End = Location


class FoursquareAccountToLocation(metaclass=Link):
    name = Utils.make_link_name(FoursquareAccount, Location)

    Value = Attributes.System.Value

    Begin = FoursquareAccount
    End = Location


class GithubAccountToLocation(metaclass=Link):
    name = Utils.make_link_name(GithubAccount, Location)

    Value = Attributes.System.Value

    Begin = GithubAccount
    End = Location


class TwitterAccountToLocation(metaclass=Link):
    name = Utils.make_link_name(TwitterAccount, Location)

    Value = Attributes.System.Value

    Begin = TwitterAccount
    End = Location


class MyspaceAccountToLocation(metaclass=Link):
    name = Utils.make_link_name(MyspaceAccount, Location)

    Value = Attributes.System.Value

    Begin = MyspaceAccount
    End = Location


class WebcamToIP(metaclass=Link):
    name = Utils.make_link_name(Webcam, IP)

    Value = Attributes.System.Value

    Begin = Webcam
    End = IP


class AddressToPerson(metaclass=Link):
    name = Utils.make_link_name(Address, Person)

    Value = Attributes.System.Value

    Begin = Address
    End = Person


class AddressToSchool(metaclass=Link):
    name = Utils.make_link_name(Address, School)

    Value = Attributes.System.Value

    Begin = Address
    End = School


class AddressToUniversity(metaclass=Link):
    name = Utils.make_link_name(Address, University)

    Value = Attributes.System.Value

    Begin = Address
    End = University


class AddressToWork(metaclass=Link):
    name = Utils.make_link_name(Address, Work)

    Value = Attributes.System.Value

    Begin = Address
    End = Work


class CarToCarRecord(metaclass=Link):
    name = Utils.make_link_name(Car, CarRecord)

    Value = Attributes.System.Value

    Begin = Car
    End = CarRecord


class CarToOrganisation(metaclass=Link):
    name = Utils.make_link_name(Car, Organisation)

    Value = Attributes.System.Value

    Begin = Car
    End = Organisation


class CarToPerson(metaclass=Link):
    name = Utils.make_link_name(Car, Person)

    Value = Attributes.System.Value

    Begin = Car
    End = Person


class PhoneNumberToOrganisation(metaclass=Link):
    name = Utils.make_link_name(PhoneNumber, Organisation)

    Value = Attributes.System.Value

    Begin = PhoneNumber
    End = Organisation


class PhoneNumberToWork(metaclass=Link):
    name = Utils.make_link_name(PhoneNumber, Work)

    Value = Attributes.System.Value

    Begin = PhoneNumber
    End = Work


class PhoneNumberToSchool(metaclass=Link):
    name = Utils.make_link_name(PhoneNumber, School)

    Value = Attributes.System.Value

    Begin = PhoneNumber
    End = School


class PhoneNumberToUniversity(metaclass=Link):
    name = Utils.make_link_name(PhoneNumber, University)

    Value = Attributes.System.Value

    Begin = PhoneNumber
    End = University


class IPToWork(metaclass=Link):
    name = Utils.make_link_name(IP, Work)

    Value = Attributes.System.Value

    Begin = IP
    End = Work


class IPToSkypeAccount(metaclass=Link):
    name = Utils.make_link_name(IP, SkypeAccount)

    Value = Attributes.System.Value

    Begin = IP
    End = SkypeAccount


class IPToFacebookAccount(metaclass=Link):
    name = Utils.make_link_name(IP, FacebookAccount)

    Value = Attributes.System.Value

    Begin = IP
    End = FacebookAccount


class IPToWhatsappAccount(metaclass=Link):
    name = Utils.make_link_name(IP, WhatsappAccount)

    Value = Attributes.System.Value

    Begin = IP
    End = WhatsappAccount


class IPToLinkedinAccount(metaclass=Link):
    name = Utils.make_link_name(IP, LinkedinAccount)

    Value = Attributes.System.Value

    Begin = IP
    End = LinkedinAccount


class IPToIcqAccount(metaclass=Link):
    name = Utils.make_link_name(IP, IcqAccount)

    Value = Attributes.System.Value

    Begin = IP
    End = IcqAccount


class IPToGooglePlusAccount(metaclass=Link):
    name = Utils.make_link_name(IP, GooglePlusAccount)

    Value = Attributes.System.Value

    Begin = IP
    End = GooglePlusAccount


class IPToFlickrAccount(metaclass=Link):
    name = Utils.make_link_name(IP, FlickrAccount)

    Value = Attributes.System.Value

    Begin = IP
    End = FlickrAccount


class IPToFoursquareAccount(metaclass=Link):
    name = Utils.make_link_name(IP, FoursquareAccount)

    Value = Attributes.System.Value

    Begin = IP
    End = FoursquareAccount


class IPToGithubAccount(metaclass=Link):
    name = Utils.make_link_name(IP, GithubAccount)

    Value = Attributes.System.Value

    Begin = IP
    End = GithubAccount


class IPToTwitterAccount(metaclass=Link):
    name = Utils.make_link_name(IP, TwitterAccount)

    Value = Attributes.System.Value

    Begin = IP
    End = TwitterAccount


class IPToMyspaceAccount(metaclass=Link):
    name = Utils.make_link_name(IP, MyspaceAccount)

    Value = Attributes.System.Value

    Begin = IP
    End = MyspaceAccount


class PhoneNumberToSkypeAccount(metaclass=Link):
    name = Utils.make_link_name(PhoneNumber, SkypeAccount)

    Value = Attributes.System.Value

    Begin = PhoneNumber
    End = SkypeAccount


class PhoneNumberToFacebookAccount(metaclass=Link):
    name = Utils.make_link_name(PhoneNumber, FacebookAccount)

    Value = Attributes.System.Value

    Begin = PhoneNumber
    End = FacebookAccount


class PhoneNumberToTelegramAccount(metaclass=Link):
    name = Utils.make_link_name(PhoneNumber, TelegramAccount)

    Value = Attributes.System.Value

    Begin = PhoneNumber
    End = TelegramAccount


class PhoneNumberToWhatsappAccount(metaclass=Link):
    name = Utils.make_link_name(PhoneNumber, WhatsappAccount)

    Value = Attributes.System.Value

    Begin = PhoneNumber
    End = WhatsappAccount


class PhoneNumberToLinkedinAccount(metaclass=Link):
    name = Utils.make_link_name(PhoneNumber, LinkedinAccount)

    Value = Attributes.System.Value

    Begin = PhoneNumber
    End = LinkedinAccount


class PhoneNumberToIcqAccount(metaclass=Link):
    name = Utils.make_link_name(PhoneNumber, IcqAccount)

    Value = Attributes.System.Value

    Begin = PhoneNumber
    End = IcqAccount


class PhoneNumberToGooglePlusAccount(metaclass=Link):
    name = Utils.make_link_name(PhoneNumber, GooglePlusAccount)

    Value = Attributes.System.Value

    Begin = PhoneNumber
    End = GooglePlusAccount


class PhoneNumberToFlickrAccount(metaclass=Link):
    name = Utils.make_link_name(PhoneNumber, FlickrAccount)

    Value = Attributes.System.Value

    Begin = PhoneNumber
    End = FlickrAccount


class PhoneNumberToFoursquareAccount(metaclass=Link):
    name = Utils.make_link_name(PhoneNumber, FoursquareAccount)

    Value = Attributes.System.Value

    Begin = PhoneNumber
    End = FoursquareAccount


class PhoneNumberToGithubAccount(metaclass=Link):
    name = Utils.make_link_name(PhoneNumber, GithubAccount)

    Value = Attributes.System.Value

    Begin = PhoneNumber
    End = GithubAccount


class PhoneNumberToTwitterAccount(metaclass=Link):
    name = Utils.make_link_name(PhoneNumber, TwitterAccount)

    Value = Attributes.System.Value

    Begin = PhoneNumber
    End = TwitterAccount


class PhoneNumberToMyspaceAccount(metaclass=Link):
    name = Utils.make_link_name(PhoneNumber, MyspaceAccount)

    Value = Attributes.System.Value

    Begin = PhoneNumber
    End = MyspaceAccount


class WebcamToPerson(metaclass=Link):
    name = Utils.make_link_name(Webcam, Person)

    Value = Attributes.System.Value

    Begin = Webcam
    End = Person


class WebcamToOrganisation(metaclass=Link):
    name = Utils.make_link_name(Webcam, Organisation)

    Value = Attributes.System.Value

    Begin = Webcam
    End = Organisation


class WebcamToWork(metaclass=Link):
    name = Utils.make_link_name(Webcam, Work)

    Value = Attributes.System.Value

    Begin = Webcam
    End = Work


class WebcamToSchool(metaclass=Link):
    name = Utils.make_link_name(Webcam, School)

    Value = Attributes.System.Value

    Begin = Webcam
    End = School


class WebcamToUniversity(metaclass=Link):
    name = Utils.make_link_name(Webcam, University)

    Value = Attributes.System.Value

    Begin = Webcam
    End = University


class NetworkInterfaceToPerson(metaclass=Link):
    name = Utils.make_link_name(NetworkInterface, Person)

    Value = Attributes.System.Value

    Begin = NetworkInterface
    End = Person


class NetworkInterfaceToOrganisation(metaclass=Link):
    name = Utils.make_link_name(NetworkInterface, Organisation)

    Value = Attributes.System.Value

    Begin = NetworkInterface
    End = Organisation


class NetworkInterfaceToWork(metaclass=Link):
    name = Utils.make_link_name(NetworkInterface, Work)

    Value = Attributes.System.Value

    Begin = NetworkInterface
    End = Work


class NetworkInterfaceToSchool(metaclass=Link):
    name = Utils.make_link_name(NetworkInterface, School)

    Value = Attributes.System.Value

    Begin = NetworkInterface
    End = School


class NetworkInterfaceToUniversity(metaclass=Link):
    name = Utils.make_link_name(NetworkInterface, University)

    Value = Attributes.System.Value

    Begin = NetworkInterface
    End = University


class NetworkInterfaceToAPT(metaclass=Link):
    name = Utils.make_link_name(NetworkInterface, APT)

    Value = Attributes.System.Value

    Begin = NetworkInterface
    End = APT


class URLToPerson(metaclass=Link):
    name = Utils.make_link_name(URL, Person)

    Value = Attributes.System.Value

    Begin = URL
    End = Person


class URLToOrganisation(metaclass=Link):
    name = Utils.make_link_name(URL, Organisation)

    Value = Attributes.System.Value

    Begin = URL
    End = Organisation


class URLToWork(metaclass=Link):
    name = Utils.make_link_name(URL, Work)

    Value = Attributes.System.Value

    Begin = URL
    End = Work


class URLToSchool(metaclass=Link):
    name = Utils.make_link_name(URL, School)

    Value = Attributes.System.Value

    Begin = URL
    End = School


class URLToUniversity(metaclass=Link):
    name = Utils.make_link_name(URL, University)

    Value = Attributes.System.Value

    Begin = URL
    End = University


class URLToAPT(metaclass=Link):
    name = Utils.make_link_name(URL, APT)

    Value = Attributes.System.Value

    Begin = URL
    End = APT


class URLToDomain(metaclass=Link):
    name = Utils.make_link_name(URL, Domain)

    Value = Attributes.System.Value

    Begin = URL
    End = Domain


class HashToAPT(metaclass=Link):
    name = Utils.make_link_name(Hash, APT)

    Value = Attributes.System.Value

    Begin = Hash
    End = APT


class AutonomousSystemToOrganisation(metaclass=Link):
    name = Utils.make_link_name(AutonomousSystem, Organisation)

    Value = Attributes.System.Value

    Begin = AutonomousSystem
    End = Organisation


class AutonomousSystemToWork(metaclass=Link):
    name = Utils.make_link_name(AutonomousSystem, Work)

    Value = Attributes.System.Value

    Begin = AutonomousSystem
    End = Work


class AutonomousSystemToSchool(metaclass=Link):
    name = Utils.make_link_name(AutonomousSystem, School)

    Value = Attributes.System.Value

    Begin = AutonomousSystem
    End = School


class AutonomousSystemToUniversity(metaclass=Link):
    name = Utils.make_link_name(AutonomousSystem, University)

    Value = Attributes.System.Value

    Begin = AutonomousSystem
    End = University
    
    
class PhoneBookToPerson(metaclass=Link):
    name = Utils.make_link_name(PhoneBook, Person)

    Value = Attributes.System.Value

    Begin = PhoneBook
    End = Person


class PhoneBookToPhone(metaclass=Link):
    name = Utils.make_link_name(PhoneBook, Phone)

    Value = Attributes.System.Value

    Begin = PhoneBook
    End = Phone


class PhoneBookToPhoneNumber(metaclass=Link):
    name = Utils.make_link_name(PhoneBook, PhoneNumber)

    Value = Attributes.System.Value

    Begin = PhoneBook
    End = PhoneNumber


class PhoneBookToEmail(metaclass=Link):
    name = Utils.make_link_name(PhoneBook, Email)

    Value = Attributes.System.Value

    Begin = PhoneBook
    End = Email


class PhoneBookToOrganisation(metaclass=Link):
    name = Utils.make_link_name(PhoneBook, Organisation)

    Value = Attributes.System.Value

    Begin = PhoneBook
    End = Organisation


class PhoneBookToSkypeAccount(metaclass=Link):
    name = Utils.make_link_name(PhoneBook, SkypeAccount)

    Value = Attributes.System.Value

    Begin = PhoneBook
    End = SkypeAccount


class PhoneBookToFacebookAccount(metaclass=Link):
    name = Utils.make_link_name(PhoneBook, FacebookAccount)

    Value = Attributes.System.Value

    Begin = PhoneBook
    End = FacebookAccount


class PhoneBookToTelegramAccount(metaclass=Link):
    name = Utils.make_link_name(PhoneBook, TelegramAccount)

    Value = Attributes.System.Value

    Begin = PhoneBook
    End = TelegramAccount


class PhoneBookToWhatsappAccount(metaclass=Link):
    name = Utils.make_link_name(PhoneBook, WhatsappAccount)

    Value = Attributes.System.Value

    Begin = PhoneBook
    End = WhatsappAccount


class PhoneBookToLinkedinAccount(metaclass=Link):
    name = Utils.make_link_name(PhoneBook, LinkedinAccount)

    Value = Attributes.System.Value

    Begin = PhoneBook
    End = LinkedinAccount


class PhoneBookToIcqAccount(metaclass=Link):
    name = Utils.make_link_name(PhoneBook, IcqAccount)

    Value = Attributes.System.Value

    Begin = PhoneBook
    End = IcqAccount


class PhoneBookToGooglePlusAccount(metaclass=Link):
    name = Utils.make_link_name(PhoneBook, GooglePlusAccount)

    Value = Attributes.System.Value

    Begin = PhoneBook
    End = GooglePlusAccount


class PhoneBookToFlickrAccount(metaclass=Link):
    name = Utils.make_link_name(PhoneBook, FlickrAccount)

    Value = Attributes.System.Value

    Begin = PhoneBook
    End = FlickrAccount


class PhoneBookToFoursquareAccount(metaclass=Link):
    name = Utils.make_link_name(PhoneBook, FoursquareAccount)

    Value = Attributes.System.Value

    Begin = PhoneBook
    End = FoursquareAccount


class PhoneBookToGithubAccount(metaclass=Link):
    name = Utils.make_link_name(PhoneBook, GithubAccount)

    Value = Attributes.System.Value

    Begin = PhoneBook
    End = GithubAccount


class PhoneBookToTwitterAccount(metaclass=Link):
    name = Utils.make_link_name(PhoneBook, TwitterAccount)

    Value = Attributes.System.Value

    Begin = PhoneBook
    End = TwitterAccount


class PhoneBookToMyspaceAccount(metaclass=Link):
    name = Utils.make_link_name(PhoneBook, MyspaceAccount)

    Value = Attributes.System.Value

    Begin = PhoneBook
    End = MyspaceAccount


class SkypeAccountToOrganisation(metaclass=Link):
    name = Utils.make_link_name(SkypeAccount, Organisation)

    Value = Attributes.System.Value

    Begin = SkypeAccount
    End = Organisation


class SkypeAccountToWork(metaclass=Link):
    name = Utils.make_link_name(SkypeAccount, Work)

    Value = Attributes.System.Value

    Begin = SkypeAccount
    End = Work


class SkypeAccountToSchool(metaclass=Link):
    name = Utils.make_link_name(SkypeAccount, School)

    Value = Attributes.System.Value

    Begin = SkypeAccount
    End = School


class SkypeAccountToUniversity(metaclass=Link):
    name = Utils.make_link_name(SkypeAccount, University)

    Value = Attributes.System.Value

    Begin = SkypeAccount
    End = University


class SkypeAccountToAPT(metaclass=Link):
    name = Utils.make_link_name(SkypeAccount, APT)

    Value = Attributes.System.Value

    Begin = SkypeAccount
    End = APT


class FacebookAccountToAPT(metaclass=Link):
    name = Utils.make_link_name(FacebookAccount, APT)

    Value = Attributes.System.Value

    Begin = FacebookAccount
    End = APT


class TelegramAccountToOrganisation(metaclass=Link):
    name = Utils.make_link_name(TelegramAccount, Organisation)

    Value = Attributes.System.Value

    Begin = TelegramAccount
    End = Organisation


class TelegramAccountToWork(metaclass=Link):
    name = Utils.make_link_name(TelegramAccount, Work)

    Value = Attributes.System.Value

    Begin = TelegramAccount
    End = Work


class TelegramAccountToSchool(metaclass=Link):
    name = Utils.make_link_name(TelegramAccount, School)

    Value = Attributes.System.Value

    Begin = TelegramAccount
    End = School


class TelegramAccountToUniversity(metaclass=Link):
    name = Utils.make_link_name(TelegramAccount, University)

    Value = Attributes.System.Value

    Begin = TelegramAccount
    End = University


class TelegramAccountToAPT(metaclass=Link):
    name = Utils.make_link_name(TelegramAccount, APT)

    Value = Attributes.System.Value

    Begin = TelegramAccount
    End = APT


class WhatsappAccountToOrganisation(metaclass=Link):
    name = Utils.make_link_name(WhatsappAccount, Organisation)

    Value = Attributes.System.Value

    Begin = WhatsappAccount
    End = Organisation


class WhatsappAccountToWork(metaclass=Link):
    name = Utils.make_link_name(WhatsappAccount, Work)

    Value = Attributes.System.Value

    Begin = WhatsappAccount
    End = Work


class WhatsappAccountToSchool(metaclass=Link):
    name = Utils.make_link_name(WhatsappAccount, School)

    Value = Attributes.System.Value

    Begin = WhatsappAccount
    End = School


class WhatsappAccountToUniversity(metaclass=Link):
    name = Utils.make_link_name(WhatsappAccount, University)

    Value = Attributes.System.Value

    Begin = WhatsappAccount
    End = University


class WhatsappAccountToAPT(metaclass=Link):
    name = Utils.make_link_name(WhatsappAccount, APT)

    Value = Attributes.System.Value

    Begin = WhatsappAccount
    End = APT


class LinkedinAccountToOrganisation(metaclass=Link):
    name = Utils.make_link_name(LinkedinAccount, Organisation)

    Value = Attributes.System.Value

    Begin = LinkedinAccount
    End = Organisation


class LinkedinAccountToWork(metaclass=Link):
    name = Utils.make_link_name(LinkedinAccount, Work)

    WorkStartDate = Attributes.System.WorkStartDate
    WorkEndDate = Attributes.System.WorkEndDate

    Begin = LinkedinAccount
    End = Work


class LinkedinAccountToSchool(metaclass=Link):
    name = Utils.make_link_name(LinkedinAccount, School)

    Value = Attributes.System.Value

    Begin = LinkedinAccount
    End = School


class LinkedinAccountToUniversity(metaclass=Link):
    name = Utils.make_link_name(LinkedinAccount, University)

    EntranceYear = Attributes.System.EntranceYear
    GraduationYear = Attributes.System.GraduationYear
    AcademicDegree = Attributes.System.AcademicDegree

    Begin = LinkedinAccount
    End = University


class LinkedinAccountToAPT(metaclass=Link):
    name = Utils.make_link_name(LinkedinAccount, APT)

    Value = Attributes.System.Value

    Begin = LinkedinAccount
    End = APT


class IcqAccountToOrganisation(metaclass=Link):
    name = Utils.make_link_name(IcqAccount, Organisation)

    Value = Attributes.System.Value

    Begin = IcqAccount
    End = Organisation


class IcqAccountToWork(metaclass=Link):
    name = Utils.make_link_name(IcqAccount, Work)

    Value = Attributes.System.Value

    Begin = IcqAccount
    End = Work


class IcqAccountToSchool(metaclass=Link):
    name = Utils.make_link_name(IcqAccount, School)

    Value = Attributes.System.Value

    Begin = IcqAccount
    End = School


class IcqAccountToUniversity(metaclass=Link):
    name = Utils.make_link_name(IcqAccount, University)

    Value = Attributes.System.Value

    Begin = IcqAccount
    End = University


class IcqAccountToAPT(metaclass=Link):
    name = Utils.make_link_name(IcqAccount, APT)

    Value = Attributes.System.Value

    Begin = IcqAccount
    End = APT


class GooglePlusAccountToOrganisation(metaclass=Link):
    name = Utils.make_link_name(GooglePlusAccount, Organisation)

    Value = Attributes.System.Value

    Begin = GooglePlusAccount
    End = Organisation


class GooglePlusAccountToWork(metaclass=Link):
    name = Utils.make_link_name(GooglePlusAccount, Work)

    Value = Attributes.System.Value

    Begin = GooglePlusAccount
    End = Work


class GooglePlusAccountToSchool(metaclass=Link):
    name = Utils.make_link_name(GooglePlusAccount, School)

    Value = Attributes.System.Value

    Begin = GooglePlusAccount
    End = School


class GooglePlusAccountToUniversity(metaclass=Link):
    name = Utils.make_link_name(GooglePlusAccount, University)

    Value = Attributes.System.Value

    Begin = GooglePlusAccount
    End = University


class GooglePlusAccountToAPT(metaclass=Link):
    name = Utils.make_link_name(GooglePlusAccount, APT)

    Value = Attributes.System.Value

    Begin = GooglePlusAccount
    End = APT


class GooglePlusAccountToURL(metaclass=Link):
    name = Utils.make_link_name(GooglePlusAccount, URL)

    Value = Attributes.System.Value

    Begin = GooglePlusAccount
    End = URL


class GooglePlusAccountToFacebookAccount(metaclass=Link):
    name = Utils.make_link_name(GooglePlusAccount, FacebookAccount)

    Value = Attributes.System.Value

    Begin = GooglePlusAccount
    End = FacebookAccount


class GooglePlusAccountToLinkedinAccount(metaclass=Link):
    name = Utils.make_link_name(GooglePlusAccount, LinkedinAccount)

    Value = Attributes.System.Value

    Begin = GooglePlusAccount
    End = LinkedinAccount


class GooglePlusAccountToTwitterAccount(metaclass=Link):
    name = Utils.make_link_name(GooglePlusAccount, TwitterAccount)

    Value = Attributes.System.Value

    Begin = GooglePlusAccount
    End = TwitterAccount


class FlickrAccountToOrganisation(metaclass=Link):
    name = Utils.make_link_name(FlickrAccount, Organisation)

    Value = Attributes.System.Value

    Begin = FlickrAccount
    End = Organisation


class FlickrAccountToWork(metaclass=Link):
    name = Utils.make_link_name(FlickrAccount, Work)

    Value = Attributes.System.Value

    Begin = FlickrAccount
    End = Work


class FlickrAccountToSchool(metaclass=Link):
    name = Utils.make_link_name(FlickrAccount, School)

    Value = Attributes.System.Value

    Begin = FlickrAccount
    End = School


class FlickrAccountToUniversity(metaclass=Link):
    name = Utils.make_link_name(FlickrAccount, University)

    Value = Attributes.System.Value

    Begin = FlickrAccount
    End = University


class FlickrAccountToAPT(metaclass=Link):
    name = Utils.make_link_name(FlickrAccount, APT)

    Value = Attributes.System.Value

    Begin = FlickrAccount
    End = APT


class FoursquareAccountToOrganisation(metaclass=Link):
    name = Utils.make_link_name(FoursquareAccount, Organisation)

    Value = Attributes.System.Value

    Begin = FoursquareAccount
    End = Organisation


class FoursquareAccountToWork(metaclass=Link):
    name = Utils.make_link_name(FoursquareAccount, Work)

    Value = Attributes.System.Value

    Begin = FoursquareAccount
    End = Work


class FoursquareAccountToSchool(metaclass=Link):
    name = Utils.make_link_name(FoursquareAccount, School)

    Value = Attributes.System.Value

    Begin = FoursquareAccount
    End = School


class FoursquareAccountToUniversity(metaclass=Link):
    name = Utils.make_link_name(FoursquareAccount, University)

    Value = Attributes.System.Value

    Begin = FoursquareAccount
    End = University


class FoursquareAccountToAPT(metaclass=Link):
    name = Utils.make_link_name(FoursquareAccount, APT)

    Value = Attributes.System.Value

    Begin = FoursquareAccount
    End = APT


class GithubAccountToOrganisation(metaclass=Link):
    name = Utils.make_link_name(GithubAccount, Organisation)

    Value = Attributes.System.Value

    Begin = GithubAccount
    End = Organisation


class GithubAccountToWork(metaclass=Link):
    name = Utils.make_link_name(GithubAccount, Work)

    Value = Attributes.System.Value

    Begin = GithubAccount
    End = Work


class GithubAccountToSchool(metaclass=Link):
    name = Utils.make_link_name(GithubAccount, School)

    Value = Attributes.System.Value

    Begin = GithubAccount
    End = School


class GithubAccountToUniversity(metaclass=Link):
    name = Utils.make_link_name(GithubAccount, University)

    Value = Attributes.System.Value

    Begin = GithubAccount
    End = University


class GithubAccountToAPT(metaclass=Link):
    name = Utils.make_link_name(GithubAccount, APT)

    Value = Attributes.System.Value

    Begin = GithubAccount
    End = APT


class TwitterAccountToOrganisation(metaclass=Link):
    name = Utils.make_link_name(TwitterAccount, Organisation)

    Value = Attributes.System.Value

    Begin = TwitterAccount
    End = Organisation


class TwitterAccountToWork(metaclass=Link):
    name = Utils.make_link_name(TwitterAccount, Work)

    Value = Attributes.System.Value

    Begin = TwitterAccount
    End = Work


class TwitterAccountToSchool(metaclass=Link):
    name = Utils.make_link_name(TwitterAccount, School)

    Value = Attributes.System.Value

    Begin = TwitterAccount
    End = School


class TwitterAccountToUniversity(metaclass=Link):
    name = Utils.make_link_name(TwitterAccount, University)

    Value = Attributes.System.Value

    Begin = TwitterAccount
    End = University


class TwitterAccountToAPT(metaclass=Link):
    name = Utils.make_link_name(TwitterAccount, APT)

    Value = Attributes.System.Value

    Begin = TwitterAccount
    End = APT


class MyspaceAccountToOrganisation(metaclass=Link):
    name = Utils.make_link_name(MyspaceAccount, Organisation)

    Value = Attributes.System.Value

    Begin = MyspaceAccount
    End = Organisation


class MyspaceAccountToWork(metaclass=Link):
    name = Utils.make_link_name(MyspaceAccount, Work)

    Value = Attributes.System.Value

    Begin = MyspaceAccount
    End = Work


class MyspaceAccountToSchool(metaclass=Link):
    name = Utils.make_link_name(MyspaceAccount, School)

    Value = Attributes.System.Value

    Begin = MyspaceAccount
    End = School


class MyspaceAccountToUniversity(metaclass=Link):
    name = Utils.make_link_name(MyspaceAccount, University)

    Value = Attributes.System.Value

    Begin = MyspaceAccount
    End = University


class MyspaceAccountToAPT(metaclass=Link):
    name = Utils.make_link_name(MyspaceAccount, APT)

    Value = Attributes.System.Value

    Begin = MyspaceAccount
    End = APT
# endregion
# endregion
