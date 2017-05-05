import requests


class APIError(Exception):
    def __init__(self, status=None, error=None):
        self.status = status
        self.error = error
        message = "Status: {}, error: {}".format(self.status, error)
        super(APIError, self).__init__(message)


class AuthenticatedError(Exception):
    pass


class API(object):
    """
        Factory for creating independent users that interact with API
    """
    def __init__(self, host, token=None):
        self.host = host
        self.token = token

    def action(self, url, method='POST', headers=None, authenticated=True, **kwargs):
        if authenticated:
            if not self.token:
                raise AuthenticatedError()

            cookie = {'Cookie': 'token=' + self.token}
            if headers:
                headers.update(cookie)
            else:
                headers = cookie

        resp = requests.request(method, self.host + url, timeout=10, headers=headers, json=kwargs)

        if resp.status_code not in [200, 201]:
            raise APIError(status=resp.status_code, error=resp.text)
        return resp.json()

    def register_user(self, username=None, email=None, password=None, first_name=None, last_name=None):
        resp = self.action('/register/', authenticated=False,
                           username=username, email=email, password=password,
                           first_name=first_name, last_name=last_name)

        user_id = resp['id']
        return User(user_id=user_id, username=username, email=email, password=password,
                    first_name=first_name, last_name=last_name,
                    api=API(self.host, token=self.token))


class User(object):
    """
        User for interacting with API.
        Don't construct it directly use register_user from API
    """
    def __init__(self, user_id=None, username=None, email=None, password=None, first_name=None, last_name=None,
                 api=None):
        self.id = user_id
        self.username = username
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.api = api

    def login(self):
        resp = self.api.action('/login/', authenticated=False, username=self.username, password=self.password)
        self.api.token = resp['token']

    def post(self, text):
        resp = self.api.action('/v1/posts/', text=text)
        return resp['id']

    def like(self, post):
        self.api.action('/v1/posts/' + str(post) + '/like/')
