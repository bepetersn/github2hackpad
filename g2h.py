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
        self.user = settings.get('github_user')
        self.password = settings.get('github_password')
        self.org = settings.get('github_org')
        self.label = settings.get('github_label')
        self.projects = settings.get('github_projects')

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
            logging.error("Problem with Github: %s" % e.message)
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
        self.subdomain = settings.get('hackpad_subdomain')
        self.key = settings.get('hackpad_key')
        self.secret = settings.get('hackpad_secret')
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
            logging.error("%s" % e.message)
            return False


class Agenda(object): 

    """ Synthesis class pulling formatting, credentials, and github,
        and hackpad classes together. """

    # TODO: turn this into writer; give the hackpad more 
    #       responsibility if possible

    def __init__(self, hp, gh, formatter, settings):
        self.hp = hp
        self.gh = gh
        self.formatter = formatter
        self.settings = settings

    def load_projects(self):
        return self.settings.get('github_projects')

    def load_title(self):
        return self.settings.get('hackpad_title')

    def generate(self, date=datetime.today()):

        github_projects = self.load_projects()
        hackpad_title = self.load_title()
        title = self.formatter.write_title(hackpad_title, date)

        try:
            issues, repos = self.gh.get_filtered_issues(github_projects)
            if (issues and repos):
                content = ""
                for i, r in enumerate(repos):
                    content += self.formatter.write_section(r.name, issues[i])
            else:
                return False, False

        except StandardError as e:
            logging.error(e.message)
            return False, False

        return title, content
        

    def publish(self, date=datetime.today()):

        title, content = self.generate(date)
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


class Formatter(object):

    """ Formatting handling class """

    # TODO: turn this into github2hackpad formatter

    def __init__(self, settings):

        self.settings = settings
        self.section_sep = self.settings.get('format_section_sep')
        self.item_sep = self.settings.get('format_item_sep')


    def write_section(self, title, items):
        section = "%s%s" % (title, self.section_sep)
        for item in items:
            item = self.unpack_github_item(item)
            section += "- %s%s" % (item, self.item_sep)
        return section


    def write_title(self, title, date):
        return "%s: Week of %s" % (title, self.format_date(date))


    def unpack_github_item(self, item):
        return item.title


    def format_date(self, d):

        if d.day in (1, 21, 31):
            date_suffix = 'st'
        elif d.day in (2, 22):
            date_suffix = 'nd'
        elif d.day in (3, 23):
            date_suffix = 'rd'
        else:
            date_suffix = 'th'

        return d.strftime('%B %d{0}, %Y'.format(date_suffix))


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
            # currently should only happen if this
            # file is missing
            self.clear()


    def save(self):
        with open(self.path, 'w') as f:
            yaml.dump(self.config, f)

    # TODO: make a configure method that uses clint to interactively 
    #       get these values


    def set(self, github_user='', github_password='', github_org='', 
            github_label='', github_projects=[], hackpad_key='', 
            hackpad_secret='', hackpad_subdomain='', hackpad_title='',
            format_section_sep='\n', format_item_sep='\n'):
        
        # configure overrides that are set
        for k, v in locals().iteritems():
            if v:
                self.config[k] = v
        self.save()


    def get(self, var, default=''):
        try:
            return self.config[var]
        except LookupError as e:
            if default:
                return default
            else:
                raise Exception('%s var is not set!' % var)


    def clear(self):
        # create empty file
        open(self.path, 'w').close()


def main():

    settings = Settings()
    agenda = Agenda(
        HackpadWrapper(settings), 
        GithubWrapper(settings), 
        Formatter(settings), 
        settings
    )
    agenda.publish()

if __name__ == '__main__':
    main()