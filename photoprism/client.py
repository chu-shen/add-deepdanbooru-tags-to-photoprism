import json
from functools import wraps

import requests


INFINITE = 2**31-1


def _inspect_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        _check_for_error(response)
        response.raise_for_status()
        return response.json()
    return wrapper


class Client:
    """
    API doc:
    https://pkg.go.dev/github.com/photoprism/photoprism/internal/api
    """
    token_file = 'token.txt'
    default_domain = 'https://demo.photoprism.org'
    default_root = '/api/v1'

    def __init__(self, username=None, password=None, domain=default_domain, root=default_root, debug=False):
        if debug:
            _enable_logging()
        self.base_url = domain + root
        self.session = requests.Session()
        self.session.mount(
            'http://', requests.adapters.HTTPAdapter(pool_maxsize=50))
        self.session.mount(
            'https://', requests.adapters.HTTPAdapter(pool_maxsize=50))
        if username:
            session_data = self._create_session(
                username=username, password=password)
            self.session.headers['X-Session-ID'] = session_data['id']

    def _create_session(self, username, password):
        return self._post(
            '/session', {
                'username': username,
                'password': password
            }
        )

    def get_albums(self, count=INFINITE, **params):
        """
        count, offset, category, type=album
        """
        params['count'] = count
        return self._get('/albums', params)

    def create_album(self, title):
        return self._post('/albums', data={'Title': title})

    def add_photo_to_album(self, album_uid, photo_uid):
        return self._post(
            f'/albums/{album_uid}/photos',
            data={'photos': [photo_uid]}
        )

    def get_photos(self, count=INFINITE, **params):
        """
        count, offset, merged, country, camera, lens, label, year, month,
        color, order, public, quality
        """
        params['count'] = count
        return self._get('/photos', params)

    def get_photo(self, uid):
        return self._get('/photos/' + uid)

    def add_label_to_photo(self, photo_uid, label_name, label_uncertainty=0, label_priority=10):
        return self._post(
            f'/photos/{photo_uid}/label',
            data={
                'Name': label_name,
                'Source': 'manual',
                'Uncertainty': label_uncertainty,
                'Priority': label_priority
            }
        )

    def index_photos(self, index_path='/', index_rescan=False):
        return self._post(
            f'/index',
            data={
                'Path': index_path,
                'Rescan': index_rescan
            }
        )

    @_inspect_response
    def _get(self, url_path, params=None):
        return self.session.get(self.base_url + url_path, params=params)

    @_inspect_response
    def _post(self, url_path, data=None):
        return self.session.post(
            self.base_url + url_path,
            data=json.dumps(data)
        )


def _check_for_error(response):
    if not response.ok:
        try:
            print(response.json())
        except ValueError:
            pass


def _enable_logging():
    # https://stackoverflow.com/a/16630836
    import logging
    import http.client as http_client

    http_client.HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
