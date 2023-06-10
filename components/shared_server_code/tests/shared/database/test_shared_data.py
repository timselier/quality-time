"""Tests shared data."""

from unittest.mock import patch

import mongomock

from shared.database.shared_data import _latest_report, create_measurement, latest_metric, latest_reports
from shared.model.measurement import Measurement
from shared.model.metric import Metric
from shared.utils.type import MetricId

from tests.fixtures import METRIC_ID, METRIC_ID2, REPORT_ID, SOURCE_ID, create_report
from tests.shared.base import DataModelTestCase


class TestSharedData(DataModelTestCase):
    """Test set for shared_data."""

    database_client = "shared.initialization.database.client"
    insert_new_measurement = "shared.database.shared_data.insert_new_measurement"
    sources_exist = "shared.database.shared_data.Measurement.sources_exist"
    latest_measurement = "shared.database.shared_data.latest_measurement"
    latest_metric = "shared.database.shared_data.latest_metric"
    measurement_equals = "shared.database.shared_data.Measurement.equals"

    def setUp(self) -> None:
        """Define info that is used in multiple tests."""
        # Override to create a database fixture.
        super().setUp()

        self.metric = Metric(
            self.DATA_MODEL,
            {"type": "violations", "sources": {SOURCE_ID: {"type": "violations"}}},
            "metric_uuid",
        )
        self.measurements = [
            {"_id": 1, "start": "0", "end": "1", "sources": [], "metric_uuid": METRIC_ID},
            {"_id": 2, "start": "3", "end": "4", "sources": [], "metric_uuid": METRIC_ID},
            {"_id": 3, "start": "6", "end": "7", "sources": [], "metric_uuid": METRIC_ID},
            {"_id": 4, "start": "1", "end": "2", "sources": [], "metric_uuid": METRIC_ID2},
            {"_id": 5, "start": "4", "end": "5", "sources": [], "metric_uuid": METRIC_ID2},
            {"_id": 6, "start": "7", "end": "8", "sources": [], "metric_uuid": METRIC_ID2},
        ]

        self.measurement_data = {
            "start": "0",
            "end": "1",
            "sources": [
                {
                    "type": "sonarqube",
                    "source_uuid": SOURCE_ID,
                    "name": "Source",
                    "parameters": {"url": "https://url", "password": "password"},
                },
            ],
            "metric_uuid": METRIC_ID,
            "report_uuid": REPORT_ID,
        }

        self.client = mongomock.MongoClient()
        self.database = self.client["quality_time_db"]

    def test_latest_metrics(self):
        """Test that the latest metrics are returned."""
        self.database["reports"].insert_one(create_report(report_uuid=REPORT_ID))
        self.client["quality_time_db"]["measurements"].insert_one(
            {
                "_id": "id",
                "metric_uuid": METRIC_ID,
                "status": "red",
                "sources": [{"source_uuid": SOURCE_ID, "parse_error": None, "connection_error": None, "value": "42"}],
            },
        )
        with patch(self.database_client, return_value=self.client):
            self.assertEqual(
                Metric(self.DATA_MODEL, {"tags": [], "type": "violations"}, METRIC_ID),
                latest_metric(self.database, REPORT_ID, METRIC_ID),
            )

    def test_no_latest_metrics(self):
        """Test that None is returned for missing metrics."""
        with patch(self.database_client, return_value=self.client):
            self.assertIsNone(latest_metric(self.database, REPORT_ID, MetricId("non-existing")))

    def test_no_latest_report(self):
        """Test that None is returned for missing metrics."""
        self.assertIsNone(latest_metric(self.database, REPORT_ID, METRIC_ID))

    def test_create_measurement_without_latest_measurement(self):
        """Test that create_measurement without a latest measurement inserts new measurement."""
        with (
            patch(self.latest_metric, return_value=self.metric),
            patch(self.sources_exist, return_value=True),
            patch(self.database_client, return_value=self.client),
            patch(self.insert_new_measurement) as insert_new_measurement,
            patch(self.latest_measurement, return_value=False),
        ):
            self.database["reports"].insert_one(create_report())
            create_measurement(self.database, self.measurement_data)
            insert_new_measurement.assert_called_once()

    def test_create_measurement_with_latest_measurement(self):
        """Test that create_measurement with a latest measurement inserts new measurement."""
        with (
            patch(self.latest_metric, return_value=self.metric),
            patch(self.sources_exist, return_value=True),
            patch(self.database_client, return_value=self.client),
            patch(self.insert_new_measurement) as insert_new_measurement,
            patch(self.latest_measurement, return_value=Measurement(self.metric, self.measurement_data)),
        ):
            self.database["reports"].insert_one(create_report(metric_id=METRIC_ID))
            self.client["quality_time_db"]["measurements"].insert_one(
                {
                    "_id": "id",
                    "metric_uuid": METRIC_ID,
                    "status": "red",
                    "sources": [
                        {"source_uuid": SOURCE_ID, "parse_error": None, "connection_error": None, "value": "42"},
                    ],
                },
            )
            create_measurement(self.database, self.measurement_data)
            insert_new_measurement.assert_called_once()

    def test_create_measurement_with_no_latest_metric(self):
        """Test that create_measurement without a latest metric doesn't insert new measurement."""
        with (
            patch(self.database_client, return_value=self.client),
            patch(self.insert_new_measurement) as insert_new_measurement,
            patch("shared.database.shared_data.latest_metric", return_value=None),
        ):
            create_measurement(self.database, self.measurement_data)
            insert_new_measurement.assert_not_called()

    def test_create_measurement_without_source(self):
        """Test that create_measurement without a source doesnt insert new measurement."""
        with (
            patch(self.latest_metric, return_value=self.metric),
            patch(self.sources_exist, return_value=False),
            patch(self.database_client, return_value=self.client),
            patch(self.insert_new_measurement) as insert_new_measurement,
        ):
            self.database["reports"].insert_one(create_report())
            create_measurement(self.database, self.measurement_data)
            insert_new_measurement.assert_not_called()

    def test_create_measurement_when_its_equal(self):
        """Test that create_measurement with equal measurement doesn't insert new measurement."""
        with (
            patch(self.latest_metric, return_value=self.metric),
            patch(self.measurement_equals, return_value=True),
            patch(self.database_client, return_value=self.client),
            patch(self.insert_new_measurement) as insert_new_measurement,
        ):
            self.client["quality_time_db"]["measurements"].insert_one(
                {
                    "_id": "id",
                    "metric_uuid": METRIC_ID,
                    "status": "red",
                    "sources": [
                        {"source_uuid": SOURCE_ID, "parse_error": None, "connection_error": None, "value": "42"},
                    ],
                },
            )
            self.database["reports"].insert_one(create_report())
            create_measurement(self.database, self.measurement_data)
            insert_new_measurement.assert_not_called()

    def test__latest_report(self):
        """Test that _latest_report returns latest report."""
        with patch(self.database_client, return_value=self.client):
            self.assertIsNone(_latest_report(self.database, REPORT_ID))
            self.database["reports"].insert_one(create_report(report_uuid=REPORT_ID))
            self.assertEqual(_latest_report(self.database, REPORT_ID)["report_uuid"], "report_uuid")

    def test_latest_reports(self):
        """Test that latest reports returns list of latest reports."""
        with patch(self.database_client, return_value=self.client):
            self.assertFalse(latest_reports(self.database))
            self.database["reports"].insert_one(create_report(report_uuid=REPORT_ID))
            self.database["reports"].insert_one(create_report(report_uuid=REPORT_ID, last=False, title="Not last"))
            self.assertEqual(latest_reports(self.database)[0]["report_uuid"], "report_uuid")
            self.assertEqual(len(latest_reports(self.database)), 1)
