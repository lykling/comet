#!/usr/bin/env python3
"""Qweather api backend
"""
import functools
import time
import pathlib
import jwt
import requests


class QWeather:
    DEFAULT_API = '/v7/weather/now'

    def __init__(self,
                 sub=None,
                 kid=None,
                 alg=None,
                 private_key_path=None,
                 endpoint=None,
                 api=DEFAULT_API,
                 **kwargs):
        """Initialize QWeather with an API key and endpoint."""
        self.sub = sub
        self.kid = kid
        self.alg = alg
        self.private_key_path = private_key_path
        self.private_key = pathlib.Path(
            private_key_path).expanduser().read_text()
        self.endpoint = endpoint
        self.api = api
        self.opts = kwargs

    def download_cities_data(self, savepath):
        """download cities data
        """
        targetpath = pathlib.Path(savepath).expanduser()
        url = self.opts.get(
            'cities_reference_download_url',
            'https://raw.githubusercontent.com/qwd/LocationList/refs/heads/master/China-City-List-latest.csv'
        )

        targetpath.parent.mkdir(parents=True, exist_ok=True)

        with requests.get(url, stream=True) as resp:
            resp.raise_for_status()
            with open(targetpath, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)

    @functools.cache
    def weather_cities_data(self, filepath=None):
        """load cities data
        """
        if not filepath:
            filepath = pathlib.Path(
                self.opts.get(
                    'cities_reference_path',
                    '~/.config/yycli/data/China-City-List-latest.csv'))

        targetpath = pathlib.Path(filepath).expanduser()

        if not targetpath.is_file():
            self.download_cities_data(filepath.as_posix())

        with open(targetpath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            sheet = [line.strip().split(',') for line in lines[2:]]
        return sheet

    @functools.cache
    def lookup_area_name_by_location_id(self, location_id):
        for row in self.weather_cities_data():
            if row[0] == location_id:
                return row[2]
        return ''

    @functools.cache
    def resolve_query(self, query: str):
        for row in self.weather_cities_data():
            if row[0] == query or row[1] == query or row[2].startswith(query):
                return row[0]

    def get_weather_data(self, **params):
        """get weather data
        """
        jwt_headers = {
            'kid': self.kid,
            'alg': self.alg,
        }
        jwt_payload = {
            'sub': self.sub,
            'iat': int(time.time()) - 30,
            'exp': int(time.time()) + 300,
        }
        jwt_token = jwt.encode(jwt_payload,
                               self.private_key,
                               algorithm=self.alg,
                               headers=jwt_headers)

        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.get(f'{self.endpoint}/{self.api}',
                                headers=headers,
                                params=params)
        response.raise_for_status()
        return response.json()

    def query_weather(self, query):
        """query weather by location
        """
        location_id = self.resolve_query(query)
        location_name = self.lookup_area_name_by_location_id(location_id)
        params = {
            'location': location_id,
        }
        data = self.get_weather_data(**params)
        return {
            'area': location_name,
            'phenomenon': data['now']['text'],
            'temperature': data['now']['temp'],
            'wind_direction': data['now']['windDir'],
            'wind_class': data['now']['windScale'],
        }
