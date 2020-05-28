import asyncio
from collections import OrderedDict
from datetime import date, datetime

import requests
import requests.auth

headers = {'content-type': 'application/json', 'accept': 'application/json'}

__all__ = ['Client']

_TS_FORMATS = [
    '%Y-%m-%d %H:%M:%S.%f',
    '%Y-%m-%d %H:%M:%S',
    '%Y-%m-%d %H:%M',  # these 2 are not as originally doc'd,
    '%Y-%m-%d %H',     # but match previous pandas behavior
    '%Y-%m-%d',
    '%Y-%m',
    '%Y']


def ensure_time(time):
    if isinstance(time, datetime):
        pass
    elif isinstance(time, date):
        time = datetime.fromisoformat(time.isoformat())
    elif isinstance(time, float) or isinstance(time, int):
        time = datetime.fromtimestamp(time)
    else:
        for fmt in _TS_FORMATS:
            try:
                time = datetime.strptime(time, fmt)
                break
            except ValueError:
                pass
        else:
            raise ValueError("Your time is in wrong format.")

    return time.isoformat(sep=' ', timespec='milliseconds')


class UncaughtServerError(Exception):
    pass

class Client:
    def __init__(self, url, user, password):
        """
        url : string
            base URL, such as ``'https://some_host:port/Olog'``
        user : string
        password : string
        """
        if url.endswith('/'):
            url = url[:-1]
        self.user = user
        auth = requests.auth.HTTPBasicAuth(user, password)
        self._url = url
        self._session = requests.Session()
        # I have requested that working certificates be properly configured on
        # the server. This is unfortunately a necessary workaround for now....
        self._session.verify = False
        self._kwargs = dict(headers=headers, auth=auth)  # for every request

    def check_owner(self, d):
        # This function checks whether value of 'owner' match user of client.
        # It has to be true based on server requirments.
        if 'owner' in d and d['owner'] != self.user:
            raise ValueError(f"Server only accept current user: {self.user} as \
                             value of owner")

    # Logbooks
    def get_logbooks(self):
        url = f'{self._url}/logbooks'
        res = self._session.get(url, **self._kwargs)
        res.raise_for_status()
        return res.json()

    def get_logbook(self, name):
        # Logbooks have an integer id, but this REST endpoint expects the
        # *name*.  It does not accept an id.
        url = f'{self._url}/logbooks/{name}'
        res = self._session.get(url, **self._kwargs)
        res.raise_for_status()
        return res.json()

    def put_logbooks(self, logbooks):
        url = f'{self._url}/logbooks'
        res = self._session.put(url, json=logbooks, **self._kwargs)
        res.raise_for_status()

    def put_logbook(self, logbook):
        self.check_owner(logbook)
        url = f'{self._url}/logbooks/{logbook["name"]}'
        res = self._session.put(url, json=logbooks, **self._kwargs)
        res.raise_for_status()
        # The server returned OK. Its response contains a copy of what it
        # inserted into its database. We can compare it with our submission for
        # extra verification that everything worked correctly.
        logbook_from_server = res.json()
        logbook_cp = logbook.copy()
        if logbook_cp != logbook_from_server:
            raise UncaughtServerError(f"No http error was raised but server \
                                      doesn't successfully put logbook you \
                                      want. Server put {res.json()} while you \
                                      are tring to put {logbook}.")
        return res.json()


    # Logs
    def get_logs(self, desc=None, fuzzy=None, phrase=None, owner=None,
                 start=None, end=None, includeevents=None,
                 logbooks=None, tags=None, properties=None):

        """
        desc : a list of str
            A list of keywords which are present in the log entry description

        fuzzy : str
            Allow fuzzy searches

        phrase: str
            Finds log entries with the exact same word/s

        owner: str
            Finds log entries with the given owner

        start : class 'datetime.datetime'
            Search for log entries created after given time instant

        end : class 'datetime.datetime'
            Search for log entries created before the given time instant

        includeevents : class 'datetime.datetime'
            A flag to include log event times when

        tags : str
            Search for log entries with at least one of the given tags

        logbooks : str
            Search for log entries with at least one of the given logbooks
        """
        if start is not None:
            start = ensure_time(start)
        if end is not None:
            end = ensure_time(end)
        params = dict(desc=desc, fuzzy=fuzzy, phrase=phrase, owner=owner,
                      start=start, end=end, includeevents=includeevents,
                      logbooks=logbooks, tags=tags, properties=properties)
        params = {k: v for k, v in params.items() if v is not None}
        url = f'{self._url}/logs'
        res = self._session.get(url, params=params, **self._kwargs)
        res.raise_for_status()
        return res.json()

    def get_log(self, id):
        url = f'{self._url}/logs/{id}'
        res = self._session.get(url, **self._kwargs)
        res.raise_for_status()
        return res.json()


    # Attachments
    def get_attachment(self, id, filename):
        url = f'{self._url}/logs/attachments/{id}/{filename}'
        res = self._session.get(url, **self._kwargs)
        return res.content


    def post_attachment(self, id, files):
        url = f'{self._url}/logs/attachments/{id}'
        res = self._session.post(url, files=files, **self._kwargs)
        res.raise_for_status()


    # Tags
    def get_tags(self):
        url = f'{self._url}/tags'
        res = self._session.get(url, **self._kwargs)
        res.raise_for_status()
        return res.json()


    def get_tag(self, name):
        url = f'{self._url}/tags/{name}'
        res = self._session.get(url, **self._kwargs)
        res.raise_for_status()
        return res.json()


    def put_tags(self, tags):
        url = f'{self._url}/tags'
        res = self._session.put(url, json=tags, **self._kwargs)
        res.raise_for_status()


    def put_tag(self, tag):
        url = f'{self._url}/tags/{tag["name"]}'
        res = self._session.put(url, json=tag, **self._kwargs)
        res.raise_for_status()
        # The server returned OK. Its response contains a copy of what it
        # inserted into its database. We can compare it with our submission for
        # extra verification that everything worked correctly.
        if tag != res.json():
            raise UncaughtServerError(f"No http error was raised but server \
                                      doesn't successfully put tag you want.\
                                      Server put {res.json()} while you are \
                                      tring to put {tag}.")
        return res.json()


    # Properties
    def get_properties(self):
        url = f'{self._url}/properties'
        res = self._session.get(url, **self._kwargs)
        res.raise_for_status()
        return res.json()


    def get_property(self, name):
        url = f'{self._url}/properties/{name}'
        res = self._session.get(url, **self._kwargs)
        res.raise_for_status()
        return res.json()


    def put_properties(self, properties):
        url = f'{self._url}/properties'
        res = self._session.put(url, json=properties, **self._kwargs)
        res.raise_for_status()


    def put_property(self, property):
        self.check_owner(property)
        url = f'{self._url}/properties/{property["name"]}'
        res = self._session.put(url, json=property, **self._kwargs)
        res.raise_for_status()
        # The server returned OK. Its response contains a copy of what it
        # inserted into its database. We can compare it with our submission for
        # extra verification that everything worked correctly.
        property_from_server = res.json()
        property_cp = property.copy()
        property_cp['attributes'] = sorted(property_cp['attributes'],
                                           key=lambda d: d['name'])
        if OrderedDict(property_cp) != property_from_server:
            raise UncaughtServerError(f"No http error was raised but server \
                                      doesn't successfully put property you \
                                      want. Server puts {res.json()} while \
                                      you are tring to put {property}.")
        return res.json()

