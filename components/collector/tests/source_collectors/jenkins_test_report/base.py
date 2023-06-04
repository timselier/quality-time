"""Base classes for Jenkins test report unit tests."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class JenkinsTestReportTestCase(SourceCollectorTestCase):
    """Base class for Jenkins test report unit tests."""

    SOURCE_TYPE = "jenkins_test_report"
