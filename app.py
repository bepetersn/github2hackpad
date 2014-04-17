from github import Github
from github.GithubException import GithubException
from hackpad_api.hackpad import Hackpad
from datetime import datetime

import yaml

class GithubWrapper(object):

    """ This class provides a simplistic front-end interface to the Github API,
        mostly for accessing issues. Allows some filtering of these based on org, repo,
        and label. """

    def __init__(self, settings, testing_session=None):
        self.user = settings.config['github_user']
        self.password = settings.config['github_password']
        self.org = settings.config['github_org']
        self.label = settings.config['github_label']
        self.projects = settings.config['github_projects']

        if testing_session:
           self.session = testing_session
        else:
            self.session = Github(self.user, self.password)

    def issues_by_repos(self, org='', projects=[],
                            label=''):

        """
            Returns a list of repos and a corresponding list of
            tuples of those repos' issues, filtered by the label
            defined in GithubWrapper's settings. 

            Defaults to using the settings-defined org, projects, and label,
            but this can be overrided with this function. """

        if not org:
            org = self.org
        if not projects:
            projects = self.projects
        if not label:
            label = self.label

        filtered_repos = set([])
        filtered_issues = set([])

        try:
            org = self.session.get_organization(self.org)
            all_repos = org.get_repos()

            for r in all_repos:
                print "all: " + r.name
                if self.filter_repo_by_include(r, self.projects):
                    print "included: " + r.name
                    filtered_repos.add(r)

            for r in filtered_repos:
                if r.has_issues and not r.private:
                    result = self.filter_issues_by_label(r.get_issues(), self.label)
                    filtered_issues.add(tuple(result))

        except GithubException as e:
            print("Problem with Github: ", e.message)
        except StandardError as e:
            print(e.message)

        return filtered_repos, filtered_issues

    def filter_repo_by_include(self, repo, include_repos):
        return repo.name in include_repos

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
            issues = self.gh.issues_by_repos(self.settings)
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

        try:
            with open(self.path, 'r') as f:
                self.config = yaml.load(f)
        except IOError:
            try:
                # create empty file
                open(self.path, 'w').close()
            except IOError as e:
                self.config = {}
        finally:
            if self.config is None:
                self.config = {}


    def save(self):
        with open(self.path, 'w') as f:
            yaml.dump(self.config, f)

    def configure(self, github_user='', github_password='', hackpad_key='', 
                    hackpad_secret='', github_org='sc3', github_label='in progress', 
                        github_projects=['sc3', 'cookcountyjail', 
                        '26thandcalifornia', 'django-townsquare']):
        
        if github_user:
            self.config['github_user'] = github_user
        if github_password:
            self.config['github_password'] = github_password
        if hackpad_key:
            self.config['hackad_key'] = hackpad_key 
        if hackpad_secret:
            self.config['hackpad_secret'] = hackpad_secret

        self.config['github_org'] = github_org
        self.config['github_label'] = github_label
        self.config['github_projects'] = github_projects

        # NEED MORE STUFF!

        self.save()


def main():

    # Move all this explict, ugly calling of settings somewhere more quaint

    settings = Settings()
    messages = Messages({'item_slice_point': '120'})
    settings.configure()
    hp = HackpadWrapper(settings)
    gh = GithubWrapper(settings)
    agenda = Agenda(hp, gh, messages, settings)
    agenda.publish(datetime.now())
    # define default projects in settings

if __name__ == '__main__':
    main()