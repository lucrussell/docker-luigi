import json

import luigi
import luigi.interface
import re
from luigi.configuration import add_config_path
from luigi.mock import MockTarget

from tests.mock_tasks import FetchUserListMock, FetchFollowingsMock, FetchUserProfileMock, ExtractUserMetricsMock


def test_fetch_user_list(requests_mock):
    MockTarget.fs.clear()
    add_config_path('testconfig/luigi.conf')
    with open('data/publication_response.json') as input_file:
        url = re.compile("https://medium.com/*.*")
        requests_mock.register_uri(method='GET', url=url, text=input_file.read())
        luigi.build([FetchUserListMock()], local_scheduler=True, no_lock=True, workers=1)
        assert 1 == requests_mock.call_count
        r = json.loads(MockTarget.fs.get_data('/tmp/a.txt'))
        assert 10 == len(r)


def test_fetch_user_profiles(mocker, requests_mock):
    MockTarget.fs.clear()
    add_config_path('testconfig/luigi.conf')
    with open('data/user_profile_response.json') as input_file:
        mocker.patch('luigi.Task.input', return_value=luigi.LocalTarget("data/user_list.json"))
        url = re.compile("https://medium.com/*.*")
        requests_mock.register_uri(method='GET', url=url, text=input_file.read())

        luigi.build([FetchUserProfileMock(file_number=0)], local_scheduler=True, no_lock=True, workers=1)
        assert 8 == requests_mock.call_count
        r = json.loads(MockTarget.fs.get_data('/tmp/a.txt'))
        assert 8 == len(r.get("root"))


def test_fetch_user_followings(mocker, requests_mock):
    MockTarget.fs.clear()
    add_config_path('testconfig/luigi.conf')
    with open('data/user_followings_response.json') as input_file:
        mocker.patch('luigi.Task.input', return_value=luigi.LocalTarget("data/user_profile.json"))
        url = re.compile("https://medium.com/*.*")
        requests_mock.register_uri(method='GET', url=url, text=input_file.read())

        luigi.build([FetchFollowingsMock(file_number=0)], local_scheduler=True, no_lock=True, workers=1)
        assert 2 == requests_mock.call_count
        r = json.loads(MockTarget.fs.get_data('/tmp/a.txt'))
        assert 3 == len(r["root"][0]["following_list"])
        assert 3 == len(r["root"][1]["following_list"])


def test_extract_user_metrics(mocker):
    MockTarget.fs.clear()
    add_config_path('testconfig/luigi.conf')
    mocker.patch('luigi.Task.input', return_value=luigi.LocalTarget("data/user_profile.json"))

    luigi.build([ExtractUserMetricsMock(file_number=0)], local_scheduler=True, no_lock=True, workers=1)
    r = json.loads(MockTarget.fs.get_data('/tmp/a.txt'))
    assert 2 == len(r.get("root"))
