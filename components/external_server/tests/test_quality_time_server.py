"""Unit tests for the external server main script."""

import logging
import unittest
from unittest.mock import patch, Mock

from quality_time_server import serve


@patch("quality_time_server.init_database", Mock())
@patch("bottle.install", Mock())
class ExternalServerTestCase(unittest.TestCase):
    """Unit tests for starting the external server."""

    @patch("bottle.run")
    def test_start(self, mocked_run):
        """Test that the server is started."""
        serve()
        mocked_run.assert_called_once()

    @patch("bottle.run", Mock())
    def test_default_log_level(self):
        """Test the default logging level."""
        serve()
        self.assertEqual("WARNING", logging.getLevelName(logging.getLogger().getEffectiveLevel()))

    @patch("bottle.run", Mock())
    @patch("os.getenv", Mock(return_value="DEBUG"))
    def test_change_log_level(self):
        """Test that the logging level can be changed."""
        serve()
        self.assertEqual("DEBUG", logging.getLevelName(logging.getLogger().getEffectiveLevel()))
