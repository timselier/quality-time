"""Test the metric model."""

from datetime import date
import unittest

from shared.model.metric import Metric
from shared.model.measurement import Measurement
from shared.utils.functions import iso_timestamp

from tests.fixtures import METRIC_ID


class MetricTest(unittest.TestCase):
    """Test the metric model."""

    DATA_MODEL = {"metrics": {"fixture_metric_type": {"name": "fixture_metric_type", "unit": "issues"}}}

    def test_summarize_empty_metric(self):
        """Test that a minimal metric returns a summary."""
        metric = Metric(self.DATA_MODEL, {"type": "fixture_metric_type"}, METRIC_ID)

        result = metric.summarize([])
        self.assertDictEqual(
            result,
            {
                "type": "fixture_metric_type",
                "scale": "count",
                "status": None,
                "status_start": None,
                "latest_measurement": None,
                "recent_measurements": [],
                "sources": {},
            },
        )

    def test_summarize_measurements(self):
        """Test that a minimal metric returns a summary."""
        metric = Metric(self.DATA_MODEL, {"type": "fixture_metric_type"}, METRIC_ID)

        measurement_timestamp = iso_timestamp()
        measurement = Measurement(
            metric,
            count={"value": 1, "start": measurement_timestamp},
            status="target_met",
        )

        result = metric.summarize([measurement])
        self.assertDictEqual(
            result,
            {
                "issue_status": [],
                "type": "fixture_metric_type",
                "scale": "count",
                "status": "target_met",
                "status_start": None,
                "latest_measurement": {
                    "count": {"value": 1, "start": measurement_timestamp},
                    "end": measurement_timestamp,
                    "sources": [],
                    "start": measurement_timestamp,
                    "status": "target_met",
                },
                "recent_measurements": [
                    {
                        "count": {"status": "target_met", "value": 1},
                        "end": measurement_timestamp,
                        "start": measurement_timestamp,
                    }
                ],
                "sources": {},
            },
        )

    def test_summarize_metric_data(self):
        """Test that metric data is summarized."""
        metric = Metric(
            self.DATA_MODEL,
            {"type": "fixture_metric_type", "some_metric_property": "some_value"},
            METRIC_ID,
        )

        result = metric.summarize([])
        self.assertDictEqual(
            result,
            {
                "type": "fixture_metric_type",
                "scale": "count",
                "status": None,
                "status_start": None,
                "latest_measurement": None,
                "recent_measurements": [],
                "some_metric_property": "some_value",
                "sources": {},
            },
        )

    def test_summarize_metric_kwargs(self):
        """Test that metric data is summarized."""
        metric = Metric(self.DATA_MODEL, {"type": "fixture_metric_type"}, METRIC_ID)

        result = metric.summarize([], some_kw="some_arg")
        self.assertDictEqual(
            result,
            {
                "type": "fixture_metric_type",
                "scale": "count",
                "status": None,
                "status_start": None,
                "latest_measurement": None,
                "recent_measurements": [],
                "some_kw": "some_arg",
                "sources": {},
            },
        )

    def test_debt_end_date(self):
        """Test debt end date."""
        metric = Metric(self.DATA_MODEL, {"type": "fixture_metric_type"}, METRIC_ID)
        self.assertEqual(metric.debt_end_date(), date.max.isoformat())

        metric["debt_end_date"] = ""
        self.assertEqual(metric.debt_end_date(), date.max.isoformat())

        metric["debt_end_date"] = "some date"
        self.assertEqual(metric.debt_end_date(), "some date")

    def test_name(self):
        """Test that we get the metric name from the metric."""
        metric = Metric(self.DATA_MODEL, {"type": "fixture_metric_type", "name": "name"}, METRIC_ID)
        self.assertEqual("name", metric.name)

    def test_missing_name(self):
        """Test that we get the metric name from the data model if the metric has no name."""
        metric = Metric(self.DATA_MODEL, {"type": "fixture_metric_type"}, METRIC_ID)
        self.assertEqual("fixture_metric_type", metric.name)

    def test_unit(self):
        """Test that we get the metric unit from the metric."""
        metric = Metric(self.DATA_MODEL, {"type": "fixture_metric_type", "unit": "oopsies"}, METRIC_ID)
        self.assertEqual("oopsies", metric.unit)

    def test_missing_unit(self):
        """Test that we get the metric unit from the data model if the metric has no unit."""
        metric = Metric(self.DATA_MODEL, {"type": "fixture_metric_type"}, METRIC_ID)
        self.assertEqual("issues", metric.unit)
