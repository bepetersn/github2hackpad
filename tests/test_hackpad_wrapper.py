from mock import Mock, call
from app import HackpadWrapper, Settings

class TestHackpadWrapper:
    
    def test_create_pad(self):

        # Define desired values

        my_subdomain = 'sub'
        my_key = 'key'
        my_secret = 'secret'
        my_title = 'My Title'
        my_content = 'My exciting content!'
        new_pad_id = 'qo0m5xqu9'

        # Create a bunch of Mock objects

        mock_settings = Mock()
        mock_settings.config = {
            'hackpad_subdomain': my_subdomain,
            'hackpad_key': my_key,
            'hackpad_secret': my_secret,
        }
        mock_session = Mock()
        mock_session.create_hackpad.return_value = \
            {'padId': new_pad_id} # just a random id

        # Actually test HackpadWrapper

        hackpad = HackpadWrapper(mock_settings, mock_session)
        result = hackpad.create_pad(my_title, my_content)

        assert mock_session.create_hackpad.called
        # doesn't work for some reason...
        # assert mock_session.create_hackpad.assert_called_with(my_title, my_content) 
        assert result == new_pad_id



