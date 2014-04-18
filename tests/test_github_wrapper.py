from mock import Mock, call
from g2h import GithubWrapper, Settings


class TestGithubWrapper:


    def test_pull_in_one_issue_per_repo(self):

        # Define all of my test data / desired results

        my_user = 'g_user'
        my_pw = 'g_password'
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

        # Mock all the gitub APIs I'm going to use

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
            repo.private = False
            repo.has_issues = True
            repo.get_issues.return_value = [mock_issues[i]]

        mock_session.get_organization.return_value = mock_organization
        mock_organization.get_repos.return_value = mock_repos

        # Set Github-related settings
        my_settings = Mock()
        my_settings.config = {  
            'github_user': my_user, 
            'github_password': my_pw, 
            'github_org': my_org,
            'github_label': my_label,
            'github_projects': my_repo_names,
        }

        # Actually test the GithubWrapper class

        github = GithubWrapper(my_settings, testing_session=mock_session)
        issues, repos = github.get_filtered_issues()

        result_issues = [(i,) for i in mock_issues]

        assert (issues, repos) == (result_issues, mock_repos)


# TODO: Write a more complex test case with multiple issues per repo
# The above will actually fail with multiple issues per repo, but the
# logic is really onerous to write out, so I haven't done it.



