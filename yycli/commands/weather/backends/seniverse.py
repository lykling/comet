#!/usr/bin/env python3
"""Seniverse API backend
"""
import base64
import functools
import hashlib
import hmac
import pathlib
import time
import requests
import zipfile
import xlrd


class Seniverse:
    DEFAULT_ENDPOINT = 'https://api.seniverse.com'
    DEFAULT_API = '/v4'

    def __init__(self,
                 public_key: str,
                 secret_key: str,
                 endpoint=DEFAULT_ENDPOINT,
                 api=DEFAULT_API,
                 **kwargs):
        """Initialize Seniverse with a public key and endpoint."""
        self.public_key = public_key
        self.secret_key = secret_key
        self.endpoint = endpoint
        self.api = api
        self.opts = kwargs

    def download_district_id_data(self, savepath):
        """download district_id data
        """
        targetpath = pathlib.Path(savepath).expanduser()
        url = self.opts.get('district_id_reference_download_url',
                            ('https://mapopen-website-wiki.bj.bcebos.com'
                             '/cityList/weather_district_id.csv'))

        targetpath.parent.mkdir(parents=True, exist_ok=True)

        with requests.get(url, timeout=5, stream=True) as resp:
            resp.raise_for_status()
            with open(targetpath, 'wb') as fout:
                for chunk in resp.iter_content(chunk_size=8192):
                    fout.write(chunk)

    @functools.cache
    def weather_district_data(self, filepath=None):
        """load weather_district_id.csv data
        """
        if not filepath:
            filepath = pathlib.Path(
                self.opts.get('district_id_reference_path',
                              '~/.config/yycli/data/weather_district_id.csv'))

        targetpath = pathlib.Path(filepath).expanduser()

        if not targetpath.is_file():
            self.download_district_id_data(filepath.as_posix())

        with open(targetpath, 'r', encoding='utf-8') as fin:
            sheet = list(map(lambda x: x.strip().split(','), fin.readlines()))
            weather_data = sheet[1:]
            return weather_data

    def download_cities_data(self, savepath):
        """download cities data
        """
        targetpath = pathlib.Path(savepath).expanduser()
        url = self.opts.get('cities_reference_download_url',
                            ('https://cdn.sencdn.com'
                             '/download/data/thinkpage_cities.zip'))
        targetpath.parent.mkdir(parents=True, exist_ok=True)
        with requests.get(url, timeout=5, stream=True) as resp:
            resp.raise_for_status()
            with open(targetpath, 'wb') as fout:
                for chunk in resp.iter_content(chunk_size=8192):
                    fout.write(chunk)

    @functools.cache
    def cities_data(self, filepath=None):
        """load cities data from zip file
        """
        if not filepath:
            filepath = pathlib.Path(
                self.opts.get('cities_reference_path',
                              '~/.config/yycli/data/thinkpage_cities.zip'))

        targetpath = pathlib.Path(filepath).expanduser()
        if not targetpath.is_file():
            self.download_cities_data(targetpath)

        with zipfile.ZipFile(targetpath, 'r') as zf:
            # default filename in zip is cp437 encoding
            fname = '城市列表.xls'.encode('utf-8').decode('cp437')
            with zf.open(fname, 'r') as fin:
                workbook = xlrd.open_workbook(file_contents=fin.read())
                worksheet = workbook.sheet_by_index(1)
                sheet = [[
                    worksheet.cell(r, c).value for c in range(worksheet.ncols)
                ] for r in range(1, worksheet.nrows)]
                return sheet

    @functools.cache
    def lookup_weather_district_by_id(self, district_id):
        """search district in weather_district_data by district id
        """
        for row in self.weather_district_data():
            if row[5] == district_id:
                return row
        return None

    @functools.cache
    def lookup_weather_district_by_text(self, district):
        """search district in weather_district_data by district text
        """
        for row in self.weather_district_data():
            if row[4].startswith(district):
                return row
        return None

    @functools.cache
    def lookup_lonlat_by_id(self, district_id):
        """lookup longitude and latitude by district id
        """
        row = self.lookup_weather_district_by_id(district_id)
        if row:
            return (row[6], row[7])
        return ('', '')

    @functools.cache
    def lookup_district_name_by_id(self, district_id):
        """lookup district name by district id
        """
        row = self.lookup_weather_district_by_id(district_id)
        if row:
            return row[4]
        return ''

    @functools.cache
    def lookup_city_id_by_text(self, name: str):
        """lookup city id by city name or city id or city pinyin
        """
        for row in self.cities_data():
            city_id, _, alias, pinyin = row
            if name == city_id or name == pinyin or alias.split(
                    '/')[-1].startswith(name):
                return city_id
        return ''

    def resolve_query(self, query: str):
        """resolve district id
        """
        return self.lookup_city_id_by_text(query)

    def get_weather_data(self, **kwargs):
        """Get weather data from Seniverse API.
        """
        params = dict(**kwargs)
        params['public_key'] = self.public_key
        params.setdefault('ts', str(int(time.time())))
        params.setdefault('ttl', '300')
        query = "&".join(f"{key}={value}"
                         for key, value in sorted(params.items())).encode()
        params['sig'] = base64.b64encode(
            hmac.new(self.secret_key.encode(), query,
                     hashlib.sha1).digest()).decode()
        response = requests.get(f'{self.endpoint}{self.api}', params=params)
        response.raise_for_status()
        return response.json()

    def query_weather(self, query):
        """Query weather data for a district.

        Args:
            query (str): District ID or name.

        Returns:
            dict: Weather data in JSON format.
        """
        # district_id = self.resolve_query(query)
        # if not district_id:
        #     raise ValueError(f"Invalid district query: {query}")
        # area_name = self.lookup_district_name_by_id(district_id)
        # lon, lat = self.lookup_lonlat_by_id(district_id)
        city_id = self.resolve_query(query)
        data = self.get_weather_data(
            location=f'{city_id}',
            unit='c',
        )
        data['results'][0]['now'].setdefault('wind_direction', '未知')
        data['results'][0]['now'].setdefault('wind_scale', '未知')
        return {
            'area': f'{data["results"][0]["location"]["name"]}',
            'phenomenon': f'{data["results"][0]["now"]["text"]}',
            'temperature': f'{data["results"][0]["now"]["temperature"]}',
            'wind_direction': f'{data["results"][0]["now"]["wind_direction"]}',
            'wind_class': f'{data["results"][0]["now"]["wind_scale"]}',
        }
