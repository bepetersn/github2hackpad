from mock import Mock, call
from agenda import GithubWrapper


class TestGithubWrapper:


    def test_pull_in_simple_issues(self):

        my_user = 'user'
        my_pw = 'password'
        my_label = 'in progress'
        my_org = 'sc3'
        my_repo_names = ['sc3', 'cookcountyjail', 'django-townsquare', '26thandcalifornia']
        my_issue_titles = [
                'create database documentation for present information model',
                'inmate in_jail field is continuously set incorrectly by scraper',
                'V2.0 Inmate Summary should display in_jail stats',
                'some other weird thing'
        ]
        my_label_names = [
                'blah',
                'sowhat',
                'wontfix',
                'in progress',
                'things',
                'scraper',
                'admin',
                'support',
                'docs',
                'api',
                'bug',
                'feature'
        ]

        mock_session = Mock()
        mock_organization = Mock()
        mock_repos = [Mock() for r in range(4)]
        mock_issues = [Mock() for i in range(4)]
        mock_labels = [Mock() for i in range(12)]

        for i, label in enumerate(mock_labels):
            label.name = my_label_names[i]
        for i, issue in enumerate(mock_issues):
            issue.title = my_issue_titles[i]
            issue.labels = [mock_labels[3]]
        for i, repo in enumerate(mock_repos):
            repo.name = my_repo_names[i]
            repo.get_issues.return_value = [mock_issues[i]]

        mock_session.get_organization.return_value = mock_organization
        mock_organization.get_repos.return_value = mock_repos

        github = GithubWrapper(my_user, my_pw, testing_session=mock_session)
        issues = github.get_tagged_issues(my_label, mock_repos, my_org)

        assert issues == set(mock_issues)


