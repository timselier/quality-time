"""Base class for Cobertura unit tests."""

from ..source_collector_test_case import SourceCollectorTestCase


class CoberturaTestCase(SourceCollectorTestCase):
    """Base class for testing Cobertura collectors."""

    SOURCE_TYPE = "cobertura"


class CoberturaCoverageTestsMixin:
    """Tests for Cobertura coverage collectors."""

    COBERTURA_XML = "Subclass responsibility"

    async def test_uncovered_lines(self):
        """Test that the number of uncovered lines and the total number of lines are returned."""
        response = await self.collect(get_request_text=self.COBERTURA_XML)
        self.assert_measurement(response, value="4", total="10")

    async def test_zipped_report(self):
        """Test that a zipped report can be read."""
        self.set_source_parameter("url", "https://example.org/cobertura.zip")
        response = await self.collect(get_request_content=self.zipped_report(("cobertura.xml", self.COBERTURA_XML)))
        self.assert_measurement(response, value="4", total="10")
