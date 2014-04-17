from github import Github
from github.GithubException import GithubException
from hackpad_api.hackpad import Hackpad
from datetime import datetime

import yaml

class GithubWrapper(object):

    """ This class provides a simplistic front-end interface to the 
        Github API, mostly for accessing issues. Allows some filtering
        of these based on org, repo, and label. """

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

    def get_filtered_issues(self, org='', projects=[], label=''):

        """
            Returns a list of repos and a corresponding list of
            tuples of those repos' issues, filtered by the label
            defined in GithubWrapper's settings. 

            Defaults to using the settings-defined org, projects, 
            and label, but this can be overrided with this function. """

        if not org:
            org = self.org
        if not projects:
            projects = self.projects
        if not label:
            label = self.label

        filtered_repos = []
        filtered_issues = []

        try:
            org = self.session.get_organization(self.org)
            all_repos = org.get_repos()

            for r in all_repos:
                print "found repo: " + r.name
                if self.filter_repo_by_include(r, self.projects):
                    filtered_repos.append(r)

            for r in filtered_repos:
                print "trying repo: " + r.name
                if r.has_issues and not r.private:
                    print "included repo: " + r.name
                    result = self.filter_issues_by_label(
                                    r.get_issues(), self.label)
                    print "issues: " + str(list(result))
                    filtered_issues.append(tuple(result))

        except GithubException as e:
            print("Problem with Github: ", e.message)
            return False, False
        except StandardError as e:
            print(e.message)
            return False, False

        print filtered_issues, filtered_repos
        return filtered_issues, filtered_repos

    def filter_repo_by_include(self, repo, include_repos):
        return repo.name in include_repos

    def filter_issues_by_label(self, issues, label):
        filtered = []
        for i in issues:
            if label in [l.name for l in i.labels]:
                filtered.append(i)
        return filtered


class HackpadWrapper(object):

    """ This class provides the front front-end to the Hackpad API """

    def __init__(self, settings, testing_session=None):
        self.subdomain = settings.config['hackpad_subdomain']
        self.key = settings.config['hackpad_key']
        self.secret = settings.config['hackpad_secret']
        if testing_session:
            self.session = testing_session
        else:
            self.session = Hackpad(self.subdomain, 
                    self.key, self.secret)


    def create_pad(self, title, content):
        try:
            result = self.session.create_hackpad(title, content)
            if result:
               return result['padId']

        except StandardError as e:
            print(e)
            return False


class Agenda(object): 

    """ Synthesis class pulling formatting, credentials, and github,
        and hackpad classes together. """

    def __init__(self, hp, gh, messages, settings):
        self.hp = hp
        self.gh = gh
        self.messages = messages
        self.settings = settings

    def load_settings(self):
        return self.settings.config['github_projects']

    def generate(self, date=datetime.now(), projects=''):

        if not projects:
           self.projects = self.load_settings()

        title = self.messages.write_title('Active Projects', date)
        content = ""

        try:
            issues, repos = self.gh.get_filtered_issues(self.settings, projects)
            if (issues and repos):
                for i, r in enumerate(repos):
                    content += self.messages.write_section(r.name, issues[i])
            else:
                return False, False

        except StandardError as e:
            print(e)
            return False, False

        return title, content
        

    def publish(self, date=datetime.now(), projects=''):

        if not projects:
            self.projects = self.load_settings()

        title, content = self.generate(date, projects)
        if (title and content):

            try:
                result = self.hp.create_pad(title, content)
                if result:
                    print "Push to hackpad successful!"
                    return True

            except StandardError as e:
                print(e)
                return False
        else:
            return False


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

    def write_section(self, title, items):
        section = "#%s\n" % title
        for item in items:
            item = self.unpack_github_item(item)
            section += "- %s\n" % item[:120]
        return section

    def write_title(self, full_name, date):
        return "%s: Week of %s" % (full_name, 
                date.strftime('%m %d, %Y'))

class Settings(object):

    """ Credentials handling class; for to not write down my keys 
        and secrets in a public repository. """

    def __init__(self, path='/home/brian/.github2hackpad'):
        self.path = path
        self.config = {}

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

    def configure(self, github_user='', github_password='', hackpad_subdomain='',
                    hackpad_key='', hackpad_secret='', github_org='sc3', 
                    github_label='in progress', github_projects=['sc3', 
                                'cookcountyjail', '26thandcalifornia', 
                                'django-townsquare']):
        
        # fall back to settings if no overrides are set;
        # TODO: throw an error if no overrides or settings 
        if github_user:
            self.config['github_user'] = github_user
        if github_password:
            self.config['github_password'] = github_password
        if hackpad_key:
            self.config['hackad_key'] = hackpad_key 
        if hackpad_secret:
            self.config['hackpad_secret'] = hackpad_secret

        # TODO: take out the hardcoded defaults, even though this
        # isn't sensitive info.
        self.config['github_org'] = github_org
        self.config['github_label'] = github_label
        self.config['github_projects'] = github_projects

        self.save()


def main():

    # TODO: make this main function as skinny as possible

    settings = Settings()
    messages = Messages({'item_slice_point': '120'})
    settings.configure()
    hp = HackpadWrapper(settings)
    gh = GithubWrapper(settings)
    agenda = Agenda(hp, gh, messages, settings)
    agenda.publish(datetime.now())

if __name__ == '__main__':
    main()