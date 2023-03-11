"""
Test custom django management commands
"""

from unittest.mock import patch

# OperationalError is raised in psycopg2 when the db is not ready
from psycopg2 import OperationalError as Psycopg2OpError
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


# sets up a mock version of the 'check' method of the 'Command' class,
# which extends from BaseCommand
# @patch operator patches check method with a mock object -> patched_check
@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test commands."""
    # Test wait_for_db behavior when the db is already available
    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database if database is already available"""
        # When check method is called, it will return True. Ensuring that
        # the command is able to run without
        # raising any exceptions when the db is already available
        patched_check.return_value = True

        # Then it calls wait_for_db. Because the mock 'check'
        # method always returns 'True'
        # the command should exit immediately without any delays or errors
        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when getting OperationalError"""
        # Basically, the instructor tests by trial and error and finds
        # that 2 times of psycopg2 error and 3 times of operational error
        # will delay the app enough so that the database is ready
        patched_check.side_effect = [Psycopg2OpError] * 2 + \
            [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)

        patched_check.assert_called_with(databases=['default'])
