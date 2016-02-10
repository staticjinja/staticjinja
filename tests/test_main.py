try:
    import unittest.mock as mock
except ImportError:
    import mock

import staticjinja


@mock.patch('os.getcwd')
@mock.patch('staticjinja.__main__.staticjinja.make_site')
def test_main(mock_ms, mock_getcwd):
    mock_site = mock.Mock()
    mock_ms.return_value = mock_site
    mock_getcwd.return_value = '/'

    staticjinja.__main__.main()

    mock_ms.assert_called_once_with(searchpath='/templates')
    mock_site.render.assert_called_once_with(use_reloader=True)
