#!/bin/bash

# Start the external server under coverage and run the feature tests.

# We collect both the coverage of the external server and of the tests themselves
# so we can discover dead code in the tests.

mkdir -p build
export COVERAGE_RCFILE="$(pwd)"/tests/feature_tests/.coveragerc
docker compose build --progress quiet database external_server renderer frontend www
docker compose up --detach database ldap
cd components/external_server || exit
python3 -m venv venv
. venv/bin/activate
ci/pip-install.sh
coverage erase
RENDERER_HOST=localhost python tests/quality_time_external_server_under_coverage.py &> ../../build/quality_time_external_server.log &
deactivate
cd ../..
cd components/internal_server || exit
python3 -m venv venv
. venv/bin/activate
ci/pip-install.sh
coverage erase
python tests/quality_time_internal_server_under_coverage.py &> ../../build/quality_time_internal_server.log &
deactivate
cd ../..
# We need to start a second external server for the renderer. We start it after the external server under coverage so
# we can measure the coverage of the startup code, including the containers that depend on the external server.
docker compose up --detach external_server renderer frontend www
cd tests/feature_tests
python3 -m venv venv
. venv/bin/activate
ci/pip-install.sh
cd ../..
sleep 10  # Give server time to start up
coverage erase
coverage run -m behave --format pretty "${1:-tests/feature_tests/src/features}"
result=$?
kill -s TERM "$(pgrep -n -f tests/quality_time_external_server_under_coverage.py)"
kill -s TERM "$(pgrep -n -f tests/quality_time_internal_server_under_coverage.py)"
sleep 5  # Give servers time to write coverage data
if [[ "$result" -eq "0" ]]
then
  coverage combine . components/external_server components/internal_server
  coverage xml
  coverage html
  coverage report
  result=$?
fi
docker compose logs > build/containers.log
docker compose down
exit $result
