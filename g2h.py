from github import Github
from github.GithubException import GithubException
from hackpad_api.hackpad import Hackpad
from datetime import datetime

import yaml, logging, sys, os


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
                if self.filter_repo_by_include(r, self.projects):
                    filtered_repos.append(r)

            for r in filtered_repos:
                if r.has_issues and not r.private:
                    result = self.filter_issues_by_label(
                                    r.get_issues(), self.label)
                    filtered_issues.append(tuple(result))

        except GithubException as e:
            loggin.error("Problem with Github: %s" % e.message)
            return False, False
        except StandardError as e:
            logging.error(e.message)
            return False, False

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
            logging.error("%s" % e.messages)
            return False


class Agenda(object): 

    """ Synthesis class pulling formatting, credentials, and github,
        and hackpad classes together. """


    def __init__(self, hp, gh, messages, settings):
        self.hp = hp
        self.gh = gh
        self.messages = messages
        self.settings = settings


    def generate(self, date=datetime.today(), projects=''):

        if not projects:
           self.projects = self.settings.get('github_projects')

        title = self.messages.write_title('Active Projects', date)
        content = ""

        try:
            issues, repos = self.gh.get_filtered_issues(projects)
            if (issues and repos):
                for i, r in enumerate(repos):
                    content += self.messages.write_section(r.name, issues[i])
            else:
                return False, False

        except StandardError as e:
            logging.error(e.message)
            return False, False

        return title, content
        

    def publish(self, date=datetime.today(), projects=''):

        if not projects:
            self.projects = self.settings.get('github_projects')

        title, content = self.generate(date, projects)
        if (title and content):

            try:
                result = self.hp.create_pad(title, content)
                if result:
                    print("Push to hackpad successful!")
                    return True

            except StandardError as e:
                logging.error(e.message)
                return False
        else:
            logging.error("Publishing failed!")
            return False


class Messages(object):

    # TODO: Rename this class to better describe what it does

    """ Formatting handling class """


    def __init__(self, formatting={}):

        # TODO: Merge this with part of messages with settings
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


    def write_section(self, title, items):
        section = "%s\n" % title
        for item in items:
            item = self.unpack_github_item(item)
            section += "- %s\n" % item[:120]
        return section


    def write_title(self, full_name, date):
        return "%s: Week of %s" % (full_name, self.format_date(date))


    def unpack_github_item(self, item):
        return item.title


    def format_date(self, d):
        return d.strftime('%B %dth, %Y')


class Settings(object):

    """ Credentials handling class; for to not write down my keys 
        and secrets in a public repository. """


    def __init__(self, path='%s/.github2hackpad' % os.environ['HOME'],
                    config={}):
        self.path = path
        self.config = {}

        try:
            with open(self.path, 'r') as f:
                file_contents = yaml.load(f)
                if file_contents:
                    self.config = file_contents
                self.set(config)
        except IOError:
            self.clear()


    def save(self):
        with open(self.path, 'w') as f:
            yaml.dump(self.config, f)


    def set(self, github_user='', github_password='', hackpad_key='', 
                    hackpad_secret='', hackpad_subdomain='', github_org='', 
                    github_label='', github_projects=[]):
        
        # configure overrides that are set
        for k, v in locals().iteritems():
            if v:
                self.config[k] = v
        self.save()


    def get(self, var, default=''):
        try:
            return self.config[var]
        except Exception('%s var is not set!' % var) as e:
            if default:
                return default
            else:
                raise e


    def clear(self):
        # create empty file
        open(self.path, 'w').close()


def main():

    settings = Settings()
    agenda = Agenda(
        HackpadWrapper(settings), 
        GithubWrapper(settings), 
        Messages(), settings
    )
    agenda.publish()

if __name__ == '__main__':
    main()