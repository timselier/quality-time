"""Unit tests for the Azure DevOps Server source up-to-dateness collector."""

from dateutil.parser import parse

from collector_utilities.functions import days_ago

from .base import AzureDevopsTestCase


class AzureDevopsSourceUpToDatenessTest(AzureDevopsTestCase):
    """Unit tests for the Azure DevOps Server source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    def setUp(self):
        """Extend to set up test data."""
        super().setUp()
        self.timestamp = "2019-09-03T00:00:00Z"  # age of file parses actual dt, age of job parses date without hh/mm
        self.expected_age = str(days_ago(parse(self.timestamp)))
        self.build_json = dict(
            value=[
                dict(
                    path=r"\\folder",
                    name="pipeline",
                    _links=dict(web=dict(href=f"{self.url}/build")),
                    latestCompletedBuild=dict(result="failed", finishTime=self.timestamp),
                )
            ]
        )

    async def test_age_of_file(self):
        """Test that the age of the file is returned."""
        self.set_source_parameter("repository", "repo")
        self.set_source_parameter("file_path", "README.md")
        repositories = dict(value=[dict(id="id", name="repo")])
        commits = dict(value=[dict(committer=dict(date=self.timestamp))])
        response = await self.collect(get_request_json_side_effect=[repositories, commits])
        self.assert_measurement(
            response, value=self.expected_age, landing_url=f"{self.url}/_git/repo?path=README.md&version=GBmaster"
        )

    async def test_age_of_pipeline(self):
        """Test that the age of the pipeline is returned."""
        self.set_source_parameter("jobs_to_include", ["folder/pipeline"])
        response = await self.collect(get_request_json_return_value=self.build_json)
        self.assert_measurement(response, value=self.expected_age, landing_url=f"{self.url}/_build")

    async def test_no_file_path_and_no_pipelines_specified(self):
        """Test that the age of the pipelines is used if no file path and no pipelines are specified."""
        response = await self.collect(get_request_json_return_value=self.build_json)
        self.assert_measurement(response, value=self.expected_age, landing_url=f"{self.url}/_build")
