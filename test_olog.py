import olog
import os
from pathlib import Path
import vcr as _vcr


# This stashes Olog server responses in JSON files (one per test)
# so that an actual server does not have to be running.
# Authentication
cassette_library_dir = str(Path(__file__).parent / Path('cassettes'))
vcr = _vcr.VCR(
    serializer='json',
    cassette_library_dir=cassette_library_dir,
    record_mode='once',
    match_on=['uri', 'method'],
    filter_headers=['authorization']
)


RECORDED_URL = "http://10.0.137.22:8080/Olog"
# Only required if we are re-recording for VCR.
url = os.environ.get('OLOG_URL', RECORDED_URL)
user = os.environ.get('OLOG_USER', '')
password = os.environ.get('OLOG_PASSWORD', '')
cli = olog.Client(url, user, password)


# Various test parameters
LOG_ID = 1

LOGBOOKS = [{'name': 'Operations', 'owner': 'olog-logs', 'state': 'Active'},
            {'name': 'TEST', 'owner': 'olog-logs', 'state': 'Active'}]
LOGBOOK = {'name': 'Operations', 'owner': 'olog-logs', 'state': 'Active'}
LOGBOOK_NAME = 'Operations'

PROPS = [{'name': 'Ticket',
          'owner': 'olog-logs',
          'state': 'Active',
          'attributes': [{'name': 'url', 'value': None, 'state': 'Active'},
                         {'name': 'id', 'value': None, 'state': 'Active'}]},
         {'name': 'TEST',
          'owner': 'olog-logs',
          'state': 'Active',
          'attributes': [{'name': 'url', 'value': None, 'state': 'Active'},
                         {'name': 'id', 'value': None, 'state': 'Active'}]}]
PROPERTY = {'name': 'Ticket',
            'owner': 'olog-logs',
            'state': 'Active',
            'attributes': [{'name': 'url', 'value': None, 'state': 'Active'},
                           {'name': 'id', 'value': None, 'state': 'Active'}]}
PROPERTY_NAME = 'Ticket'

TAGS = [{'name': 'Fault', 'state': 'Active'},
        {'name': 'TEST', 'state': 'Active'}]
TAG = {'name': 'Fault', 'state': 'Active'}
TAG_NAME = 'Fault'

ATTACHMENT_FILE = {'file': open('README.md', 'rb'),
                   'filename': (None, 'test'),
                   'fileMetadataDescription': (None, 'This is a attachment')}
ATTACHMENT_NAME = ATTACHMENT_FILE['filename'][1]


@vcr.use_cassette()
def test_get_logbooks():
    cli.get_logbooks()


@vcr.use_cassette()
def test_get_logbook():
    cli.get_logbook(LOGBOOK_NAME)


@vcr.use_cassette()
def test_put_logbooks():
    cli.put_logbooks(LOGBOOKS)


@vcr.use_cassette()
def test_put_logbook():
    cli.put_logbook(LOGBOOK)


@vcr.use_cassette()
def test_get_logs():
    logs = cli.get_logs(logbooks=LOGBOOK_NAME)
    for log in logs:
        assert LOGBOOK_NAME == log['logbooks'][0]['name']


@vcr.use_cassette()
def test_get_log():
    assert LOG_ID == cli.get_log(LOG_ID)['id']


@vcr.use_cassette()
def test_get_attachment():
    cli.get_attachment(LOG_ID, ATTACHMENT_NAME)


@vcr.use_cassette()
def test_post_attachment():
    cli.post_attachment(1, ATTACHMENT_FILE)


@vcr.use_cassette()
def test_get_tags():
    cli.get_tags()


@vcr.use_cassette()
def test_get_tag():
    assert TAG == cli.get_tag(TAG_NAME)


@vcr.use_cassette()
def test_put_tags():
    assert TAGS == cli.put_tags(TAGS)


@vcr.use_cassette()
def test_put_tag():
    cli.put_tag(TAG)


@vcr.use_cassette()
def test_get_properties():
    cli.get_properties()


@vcr.use_cassette()
def test_get_property():
    cli.get_property(PROPERTY_NAME)


@vcr.use_cassette()
def test_put_properties():
    cli.put_properties(PROPS)


@vcr.use_cassette()
def test_put_property():
    cli.put_property(PROPERTY)
