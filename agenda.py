import PyGithub
from hackpad_api.hackpad import Hackpad


class GithubWrapper:

    def __init__(self, user, password):
        pass

    def get_tagged_issues(self, tag, projects, org):
        pass


class HackpadWrapper:

    def __init__(self, key, secret, subdomain):
        pass

    def create_pad(self, name, content):
        pass


class Agenda:

    def __init__(self, hp, gh, messages):
        pass

    def generate(self, date, tag, projects):
        pass

    def publish(self, date, projects, tag):
        pass


class Messages:

    def __init__(self, formatting={}):
        self.formatting = self.formatting
        self.section_sep = self.format_param('section_sep')
        self.item_sep = format_param('item_sep')
        self.heading_lg = self.format_param('heading_lg')
        self.heading_md = self.format_param('heading_md')
        self.heading_sm = self.format_param('heading_sm')
        self.item_slice_point = self.format_param('item_slice_point')

    def format_param(self, param, default=''):
        try:
            value = formatting[param]
        except LookupError as e:
            value = default
        finally:
            return result


class Settings:

    def __init__(self):
        pass

    def configure(self, org='sc3', tag='in progress'):
        pass

    def get_credentials(self, file):
        pass

