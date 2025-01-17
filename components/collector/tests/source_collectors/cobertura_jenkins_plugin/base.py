"""Base class for Cobertura Jenkins plugin unit tests."""

from ..source_collector_test_case import SourceCollectorTestCase


class CoberturaJenkinsPluginTestCase(SourceCollectorTestCase):
    """Cobertura Jenkins Plugin test case base class."""

    SOURCE_TYPE = "cobertura_jenkins_plugin"
