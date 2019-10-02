# -*- coding: utf8 -*-
__author__ = 'sai'
import requests
import pygeohash as pgh
import codecs
import base64
import concurrent.futures

from time import sleep as sleep_before_geturl

from random import choice as get_random_sec

PATH_TO_KEY_FILE = r"c:\LampyreExamples\Googles\key.txt"


def key_textsearch():
    return open(PATH_TO_KEY_FILE).read().strip().strip('\n')

try:
    from ontology import (
        Task, Header, HeaderCollection, Utils, Field, ValueType, SchemaLink, SchemaObject, Condition, Operations, Macro,
        MacroCollection, Schema, EnterParamCollection, SchemaCollection, GraphMappingFlags, BinaryType, Constants,
        Attributes)
except:
    pass


def return_dummy(row):
    keys = ['formatted_address', 'name_address', 'lat', 'lon', 'geohash', 'photo_data']
    _line = ';'.join(map(lambda z: str(z).upper().strip().strip("'").strip('"'), [row[k] for k in keys]))
    return hash(_line)


def text_search_google_place(text, api, logger, length_geo=6, delay=5):

    def download_photo_base64(url):
        '''
        :param url:
        :return: base64 - bytes of image
        '''
        try:
            resource = requests.get(url, stream=True)
        except:
            logger.info('exception in get data...')
        else:
            if resource.status_code == 200:
                resource.raw.decode_content = True
                image_bytes = resource.raw.read()
                encoded_image = base64.b64encode(image_bytes)
                return codecs.decode(encoded_image)

    def get_photo_google(maxwidth, refphoto, YOUR_API_KEY):
        url = 'https://maps.googleapis.com/maps/api/place/photo?maxwidth={maxwidth}&photoreference={refphoto}&key={YOUR_API_KEY}'
        photo_url = url.format(maxwidth=maxwidth, refphoto=refphoto, YOUR_API_KEY=YOUR_API_KEY)
        return download_photo_base64(photo_url)

    # magic number for sleep
    msec = [x/70 for x in range(0, 50)]
    sleep_before_geturl(get_random_sec(msec))

    logger.info("try search about - '{}'".format(text))
    get_url_text = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
    textsearch = text.replace(' ', '+')
    check = True
    mypagetoken = None
    _big_set = []
    need_try = False
    session_request = requests.Session()
    while check:

        try:
            params = {}
            if not mypagetoken:
                params['query'] = textsearch
            else:
                params['pagetoken'] = mypagetoken
                sleep_before_geturl(3)

            params['key'] = api
            page = session_request.get(get_url_text, params=params, timeout=delay)
            jsonRaw = page.json()
            status_code = page.status_code
            logger.info(', '.join([text.strip(), str(status_code)]))
        except:
            logger.info('exception in get data...')
            check = False
        else:
            if status_code == 200:
                if jsonRaw['status'] == 'OK':
                    _big_set.append(jsonRaw)
                elif jsonRaw['status'] == 'ZERO_RESULTS':
                    check = False
                elif jsonRaw['status'] == 'INVALID_REQUEST':
                    need_try = True
                if 'next_page_token' in jsonRaw:
                    mypagetoken = jsonRaw['next_page_token']
                elif need_try:
                    check = True
                else:
                    check = False
            else:
                check = False
                logger.info('errors with status code: '.format(str(status_code)))

    if len(_big_set) > 0:
        _return_results = []
        for block in _big_set:

            if block['status'] != 'ZERO_RESULTS':
                return_keys = ['formatted_address', 'name_address',
                               'lat', 'lon', 'geohash', 'photo_data',
                               'search_text']
                for row in block['results']:
                    _tmp = dict.fromkeys(return_keys)
                    if 'formatted_address' in row.keys():
                        _tmp['formatted_address'] = row['formatted_address']
                    else:
                        _tmp['formatted_address'] = ''
                    if 'name' in row.keys():
                        _tmp['name_address'] = row['name']
                    else:
                        _tmp['name_address'] = ''

                    _tmp['lat'] = row['geometry']['location']['lat']
                    _tmp['lon'] = row['geometry']['location']['lng']
                    _tmp['geohash'] = pgh.encode(_tmp['lat'],_tmp['lon'], precision=length_geo)
                    _tmp['search_text'] = text
                    if 'photos' not in row:
                        _tmp['photo_data'] = ''
                        _return_results.append(_tmp)
                    else:
                        for _photo in row['photos']:
                            height = _photo['height']
                            width = _photo['width']
                            if width > 500:
                                width = 300
                            photo_reference = get_photo_google(width, _photo['photo_reference'], api)
                            if not photo_reference:
                                photo_reference = ''
                            z = {'photo_data': photo_reference}
                            _tmp.update(z)
                            _return_results.append(_tmp)
        if len(_return_results) > 0:
            return _return_results


def thread_async_(texts, threads, length_geo, logger):
    google_key = key_textsearch()
    result_rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        future_rows = {executor.submit(text_search_google_place, text, google_key, logger, length_geo):
                           text for text in texts}
        for future in concurrent.futures.as_completed(future_rows):
            try:
                result = future.result()
                if result:
                    if isinstance(result, list):
                        result_rows.extend(result)
            except Exception as exc:
                pass
    return result_rows


class GoogleTextSearchPlaces(metaclass=Header):
    # return_keys = ['formatted_address', 'name_address', 'lat', 'lon', 'geohash', 'photo_data', 'search text']
    display_name = 'Google: search places by text'
    name_address = Field('Name address', ValueType.String)
    formatted_address = Field('Formatted address', ValueType.String)
    photo_data = Field('Photo', ValueType.String, binary_type=BinaryType.Image)
    search_text = Field('search text', ValueType.String)
    lat = Field('lat', ValueType.Float)
    lon = Field('lon', ValueType.Float)
    geohash = Field('geohash', ValueType.String)


class GoogleSearchTextPlace(Task):

    def __init__(self):
        super().__init__()
        self.info, self.error, self.result, self.api, self.api_key = [None] * 5

    def get_id(self):
        return '41b49f4a-64c1-4b4f-84e3-73448e81953d'

    def get_display_name(self):
        return 'API Google:Places'

    def get_category(self):
        return "!Examples"

    def get_headers(self):
        htable = GoogleTextSearchPlaces

        htable.set_property(htable.lat.system_name, 'latitude', True)
        htable.set_property(htable.lon.system_name, 'longitude', True)
        return HeaderCollection(htable)


    def get_enter_params(self):
        ep_coll = EnterParamCollection()
        ep_coll.add_enter_param('texts', 'Search places', ValueType.String, is_array=True,
                                required=True)
        ep_coll.add_enter_param('length_geo', 'geohash', ValueType.Integer, required=True, default_value=6)
        return ep_coll

    def execute(self, enter_params, result_writer, log_writer, temp_directory=None):
        log_writer.info(enter_params)
        _texts = list(map(lambda z: z.strip(), enter_params.texts))
        maxthreads = 6
        _rows = thread_async_(_texts, maxthreads, enter_params.length_geo, log_writer)
        rows = []
        _list_of_hash = []
        for line in _rows:
            z = return_dummy(line)
            if z not in _list_of_hash:
                rows.append(line)
                _list_of_hash.append(z)

        fields_table = GoogleTextSearchPlaces.get_fields()
        for line in rows:
            _tmp = GoogleTextSearchPlaces.create_empty()
            for field in fields_table:
                if field in line:
                    _tmp[fields_table[field]] = line[field]
            result_writer.write_line(_tmp, header_class=GoogleTextSearchPlaces)



# region Debugging
if __name__ == '__main__':
    DEBUG = True

    class EnterParamsFake:
        texts = ['Управление ФСБ РФ по Удмуртской Республике']
        length_geo = 6


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
    GoogleSearchTextPlace().execute(EnterParamsFake, WriterFake, WriterFake, None)