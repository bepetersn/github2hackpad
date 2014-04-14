from github import Github
from github.GithubException import GithubException
from hackpad_api.hackpad import Hackpad
from datetime import datetime

import yaml

class GithubWrapper(object):

    """ This class provides a simplistic front-end interface to the Github API,
        mostly for accessing issues. Allows some filtering of these based on org, repo,
        and label. """

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

        try:
            org = self.session.get_organization(org_name)
            all_repos = org.get_repos()

            for r in all_repos:
                if self.filter_repo_by_include(r, include_repos):
                    filtered_repos.add(r)
                    print [r.name for r in list(filtered_repos)]

            for r in filtered_repos:
                print r.name
                result = self.filter_issues_by_label(r.get_issues(), label)
                for issue in result:
                    filtered_issues.add(issue)
        except GithubException as e:
            pass
        except StandardError as e:
            print(e.message)

        return filtered_issues

    def filter_repo_by_include(self, repo, include_repos):
        for include in include_repos:
            yield include.name 

    def filter_issues_by_label(self, issues, label):
        for i in issues:
            if label in [l.name for l in i.labels]:
                yield i


class HackpadWrapper(object):

    """ This class provides the front front-end to the Hackpad API """

    def __init__(self, subdomain, key, secret, testing_session=None):
        self.subdomain = subdomain
        self.key = key
        self.secret = secret
        if testing_session:
            self.session = testing_session
        else:
            self.session = Hackpad(subdomain, key, secret)


    def create_pad(self, title, content):
        try:
            result = self.session.create_hackpad(title, content)
            if result:
               return result['padId']

        except StandardError as e:
            print(e)


class Agenda(object): 

    """ Synthesis class pulling formatting, credentials, and github, and hackpad classes 
        together. """

    def __init__(self, hp, gh, messages, settings):
        self.hp = hp
        self.gh = gh
        self.messages = messages
        self.settings = settings

    def generate(self, date, projects):

        title = self.messages.write_title('', 'Active Projects', date)
        content = ""
        try:
            for project in projects:
                issues = self.gh.get_filtered_issues(self.settings.config['github_label'],
                        project, self.settings.config['github_org'])
                self.messages.write_section(content, project, issues)
        except StandardError as e:
            print(e)

        return title, content
        

    def publish(self, date, projects):
        title, content = self.generate(date, projects)
        try:
            result = self.hp.create_pad(title, content)
            if result:
                print "Push to Hackpad successful!"
                return True
        except StandardError as e:
            print(e)


class Messages(object):

    """ Formatting handling class """

    def __init__(self, formatting={}):

        # Merge this with part of messages with settings
        self.formatting = formatting
        self.section_sep = self.format_param('section_sep')
        self.item_sep = self.format_param('item_sep')
        self.heading_lg = self.format_param('heading_lg')
        self.heading_md = self.format_param('heading_md')
        self.heading_sm = self.format_param('heading_sm')
        self.item_slice_point = self.format_param('item_slice_point')

    def format_param(self, param, default=''):
        try:
            value = formatting[param]
        except LookupError as e:
            pass
        finally:
            return default

    def unpack_github_item(self, item):
        return item.title

    def write_section(self, master_string, title, items):
        master_string += "#%s\n" % title
        for item in items:
            item = self.unpack_github_item(item)
            master_string += "- %s\n" % item[:120]

    def write_title(self, master_string, full_name, date):
        master_string += "%s: Week of %s" % (full_name, date.strftime('%m %d, %Y'))


class Settings(object):

    """ Credentials handling class; for to not write down my keys and secrets in a 
        public repository. """

    def __init__(self, path='/home/brian/.github2hackpad'):
        self.path = path
        self.config = {}
        try:
            with open(self.path) as f:
                self.config = yaml.load(f)
        except IOError:
            print('unsuccessful loading credentials')

    def save(self):
        with open(self.path, "w") as f:
            yaml.dump(self.config, f)

    def configure(self, org_name='sc3', label='in progress'):
        self.config['github_org'] = org_name
        self.config['github_label'] = label

        # NEED MORE STUFF!

        self.save()


def main():

    # Move all this explict, ugly calling of settings somewhere more quaint

    settings = Settings()
    messages = Messages({'item_slice_point': '120'})
    settings.configure('sc3', 'in_progress')
    hp = HackpadWrapper(settings.config['github_org'], 
                        settings.config['hackpad_key'], 
                        settings.config['hackpad_secret'])
    gh = GithubWrapper(settings.config['github_username'], 
                        settings.config['github_password'])
    agenda = Agenda(hp, gh, messages, settings)
    agenda.publish(datetime.now(), ['sc3', 'cookcountyjail', '26thandcalifornia', 'django-townsquare'])
    # define default projects in settings

if __name__ == '__main__':
    main()