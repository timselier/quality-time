"""Issue status model class."""

from dataclasses import dataclass
from typing import Optional

from collector_utilities.type import ErrorMessage, URL


@dataclass
class Issue:
    """Class representing issues."""

    issue_id: str
    created: Optional[str] = None
    updated: Optional[str] = None

    def as_dict(self) -> dict:
        """Return the issue as dict."""
        return dict(issue_id=self.issue_id, created=self.created, updated=self.updated)


class IssueStatus:  # pylint: disable=too-few-public-methods
    """Class to hold the status of issues."""

    def __init__(
        self,
        issue_id: str,
        *,
        name: str = None,
        created: str = None,
        updated: str = None,
        connection_error: ErrorMessage = None,
        parse_error: ErrorMessage = None
    ) -> None:
        self.issue = Issue(issue_id, created, updated)
        self.name = name
        self.parse_error = parse_error
        self.connection_error = connection_error
        self.api_url: Optional[URL] = None
        self.landing_url: Optional[URL] = None

    def as_dict(self) -> dict:
        """Return the issue status as dict."""
        status = dict(
            name=self.name,
            parse_error=self.parse_error,
            connection_error=self.connection_error,
            api_url=self.api_url,
            landing_url=self.landing_url,
            **self.issue.as_dict(),
        )
        return {key: value for key, value in status.items() if value}