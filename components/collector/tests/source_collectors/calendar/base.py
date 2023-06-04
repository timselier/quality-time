"""Base class for calendar collector unit tests."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class CalendarTestCase(SourceCollectorTestCase):
    """Base class for calendar collectors."""

    SOURCE_TYPE = "calendar"
