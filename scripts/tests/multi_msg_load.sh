#/bin/sh

set -e

# get absolute parent directory path of current file
CURPATH=`dirname $(realpath "$0")`
cd $CURPATH

# check environment variables are set
. ../deps/env-check.sh

# we can pass optional arguments when running this script
# available arguments are -s/--sender, -r/--receiver, -h/--help
# example: ./multi_msg_load.sh -s cosmos1f2838advrjl3c8h4kjfvfmhkh0gs0wf6cyzwu8 -r osmo1cytlejwrejz8wajslgqwczlzazxaxhf4hccly5
# python3 ./internal/load-test/multi_msg_load.py $1 $2 $3 $4
docker exec -e PYTHONPATH=/:/internal -e TEST_TYPE="$TEST_TYPE" --env-file ./env  -it $CONTAINER_NAME sh -c "python3 /internal/load-test/multi_msg_load.py"
