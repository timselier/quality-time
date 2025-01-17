"""Data models collection."""

from typing import Any

from pymongo.database import Database

from shared.database.datamodels import latest_datamodel


def default_source_parameters(database: Database, metric_type: str, source_type: str):
    """Return the source parameters with their default values for the specified metric."""
    parameters = latest_datamodel(database)["sources"].get(source_type, {}).get("parameters", {}).items()
    return {key: value["default_value"] for key, value in parameters if metric_type in value["metrics"]}


def default_metric_attributes(database: Database, metric_type: str):
    """Return the metric attributes with their default values for the specified metric type."""
    metric_types = latest_datamodel(database)["metrics"]
    defaults = metric_types[metric_type]
    return dict(
        type=metric_type,
        sources={},
        name=None,
        scale=defaults["default_scale"],
        unit=None,
        addition=defaults["addition"],
        accept_debt=False,
        debt_target=None,
        direction=None,
        target=defaults["target"],
        near_target=defaults["near_target"],
        tags=defaults["tags"],
    )


def default_subject_attributes(database: Database, subject_type: str) -> dict[str, Any]:
    """Return the default attributes for the subject."""
    subject_types = latest_datamodel(database)["subjects"]
    defaults = subject_types[subject_type]
    return dict(type=subject_type, name=None, description=defaults["description"], metrics={})
