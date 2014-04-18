from mock import Mock, call
from g2h import Settings
from pytest import raises

import os


class TestSettings:

    """ Testing the settings class! """

    def setup(self):
        self.s = Settings('/tmp/tmp_settings.yml')

    def teardown(self):
        self.s.clear()
        os.remove(self.s.path)

    def test_configure_settings(self):
        # setting github_user, then retrieving 
        # it gives you back the same
        self.s.configure(github_user='username')
        result = self.s.get('github_user')
        assert result == 'username'

    def test_get_raises_not_configured(self):
        # trying to get a github_user with a new
        # settings before setting it raises an
        # exception
        with raises(Exception):
            self.s.get('github_user')