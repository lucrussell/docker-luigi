import luigi.interface
from luigi.mock import MockTarget

from example.tasks import FetchUserList, FetchUserFollowings, FetchUserProfile, ExtractUserMetrics


class MockBaseTask(luigi.Task):

    def output(self):
        return MockTarget('/tmp/a.txt')

    def run(self):
        f = self.output().open('w')
        f.close()


class FetchUserListMock(FetchUserList):

    def requires(self):
        return [MockBaseTask()]

    def output(self):
        return MockTarget('/tmp/a.txt')


class FetchUserProfileMock(FetchUserProfile):

    def requires(self):
        return [MockBaseTask()]

    def output(self):
        return MockTarget('/tmp/a.txt')


class FetchFollowingsMock(FetchUserFollowings):

    def requires(self):
        return [MockBaseTask()]

    def output(self):
        return MockTarget('/tmp/a.txt')


class ExtractUserMetricsMock(ExtractUserMetrics):

    def requires(self):
        return [MockBaseTask()]

    def output(self):
        return MockTarget('/tmp/a.txt')
