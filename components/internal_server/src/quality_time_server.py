"""Quality-time server."""

from gevent import monkey

monkey.patch_all()

# pylint: disable=wrong-import-order,wrong-import-position

import logging
import os

import bottle

from shared.initialization.database import init_database

from initialization import init_bottle, merge_unmerged_measurements, rename_issue_lead_time


def serve() -> None:  # pragma: no feature-test-cover
    """Connect to the database and start the application server."""
    log_level = str(os.getenv("INTERNAL_SERVER_LOG_LEVEL", "WARNING"))
    logging.getLogger().setLevel(log_level)
    database = init_database()
    merge_unmerged_measurements(database)
    rename_issue_lead_time(database)
    init_bottle(database)
    server_port = os.getenv("INTERNAL_SERVER_PORT", "5002")
    bottle.run(server="gevent", host="0.0.0.0", port=server_port, reloader=True, log=logging.getLogger())  # nosec


if __name__ == "__main__":  # pragma: no feature-test-cover
    serve()
