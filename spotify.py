import requests
import urllib.parse
from requests.exceptions import HTTPError
from pprint import pprint
from keys import CLIENT_ID, CLIENT_SECRET, AUTH_CODE
import base64
import time
import json

class Spotify:

    def __init__(self, client_ID):
        self.client_ID = client_ID
        self.token_info = None
        self.base_url = 'https://api.spotify.com/v1/'

    @property
    def headers(self):
        return {'Content-Type': 'aplication/json',
                'Accept' : 'application/json',
                'Authorization': 'Bearer ' + self.token_info['access_token']}

    @staticmethod
    def persist_json(_dict):
        with open('auth_spot.json','w') as file:
            json.dump(_dict, file)

    @staticmethod
    def _make_headers(_id, _secret):
        text = _id+':'+_secret
        auth_header = base64.b64encode(text.encode('ascii'))
        return {'Authorization': 'Basic %s' % auth_header.decode('ascii')}
        
    
    def authorize(self):
        """Authorize the app on spotify to get the access code"""
        payload = {'client_id': self.client_ID,
                   'response_type': 'code',
                   'redirect_uri': 'http://localhost/',
                   'scope': 'user-modify-playback-state user-read-playback-state'}
        data = urllib.parse.urlencode(payload)
        url = 'https://accounts.spotify.com/authorize?%s' % data
        print(url)
        self.get_token(input())
    
    def get_token(self, code):
        """Exchange the auth code for the auth token"""
        payload = {'grant_type': 'authorization_code',
                   'code': code,
                   'redirect_uri': 'http://localhost/'}
        header = Spotify._make_headers(CLIENT_ID, CLIENT_SECRET)
        response = requests.post('https://accounts.spotify.com/api/token',
                                 headers=header,
                                 data=payload,
                                verify=True)
        try:
            response.raise_for_status()
            response = response.json()
            self.token_info = {'access_token' : response['access_token'],
                               'refresh_token' : response['refresh_token'],
                               'expires_at' : int(time.time()) + response['expires_in']}
            Spotify.persist_json(self.token_info)
            print('Logged in succesfully')
        except HTTPError as http_err:
            print(f'HTTP error occured {http_err}')

    def json_return(self, content, is_error=True):
        return {'status': 'ERROR' if is_error else 'OK',
                'content': content}

    def get_available_devices(self):
        url = self.base_url + 'me/player/devices'
        response = requests.get(
            url,
            headers = self.headers
        )
        devices = response.json()['devices']
        for device in devices:
            if device['is_active']:
                return device['id']

    def get_current_song(self):
        url = self.base_url + 'me/player'
        try:
            response = requests.get(
                url,
                headers = self.headers
            )
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occured {http_err}')
        else:
            content = response.json()
            return self.json_return(content['item']['name'] + ' - ' + content['item']['album']['name'], False)
    
    def search(self, track_name, first=False):
        url = self.base_url + 'search'
        try:
            response = requests.get(
                url,
                headers = self.headers,
                params= {'q': track_name,
                        'type': 'track',
                        'market': 'CL',
                        'limit': 10}
            )
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occured {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        else:
            content = response.json()
            if first:
                index = 0
            else:
                for index, song in enumerate(content['tracks']['items']):
                    print(index, '-', song['album']['artists'][0]['name'],'-', song['name'])
                index = int(input('Number of song to play: '))
            album_name = content['tracks']['items'][index]['album']['name']
            track_name = content['tracks']['items'][index]['name']
            track_id = content['tracks']['items'][index]['uri']
            return album_name, track_name, track_id

    def play(self, track_name, first=False):
        url = self.base_url + 'me/player/play'
        album, track, _id = self.search(track_name, first)
        device = self.get_available_devices()
        response = requests.put(
            url,
            json={'uris': [_id]},
            headers = self.headers
        )
        if response.status_code == 204:
            return self.json_return('Now playing ' + track + ' from ' + album)
        else:
            return self.json_return('Error', True)



if __name__ == "__main__":
    spotify = Spotify(CLIENT_ID)
    # ESTO ES TEMPORAL 
    with open('auth_spot.json', 'r') as file:
        spotify.token_info = json.load(file)
    #----
    spotify.authorize()
