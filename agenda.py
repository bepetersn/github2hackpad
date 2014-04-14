from github import Github
from hackpad_api.hackpad import Hackpad


class GithubWrapper:

    def __init__(self, user, password, testing_session=None):
        self.user = user
        self.password = password

        if testing_session:
           self.session = testing_session
        else:
            self.session = Github(self.user, self.password)

    def get_filtered_issues(self, label, include_repos, org_name):

        filtered_issues = set([])
        filtered_repos = set([])

        org = self.session.get_organization(org_name)
        all_repos = org.get_repos()

        for r in all_repos:
            if self.filter_repo_by_include(r, include_repos):
                filtered_repos.add(r)

        for r in filtered_repos:
            result = self.filter_issues_by_label(r.get_issues(), label)
            for issue in result:
                filtered_issues.add(issue)

        return filtered_issues

    def filter_repo_by_include(self, repo, include_repos):
        for include in include_repos:
            yield include.name 

    def filter_issues_by_label(self, issues, label):
        for i in issues:
            if label in [l.name for l in i.labels]:
                yield i


class HackpadWrapper:

    def __init__(self, key, secret, subdomain):
        pass

    def create_pad(self, name, content):
        return None


class Agenda:

    def __init__(self, hp, gh, messages):
        pass

    def generate(self, date, tag, projects):
        return

    def publish(self, date, projects, tag):
        return


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

    def configure(self, org_name='sc3', label='in progress'):
        return 

    def get_credentials(self, file):
        return

