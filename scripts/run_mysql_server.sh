#/bin/bash

SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)"
APP_ROOT="$(dirname $SCRIPT_PATH)"
DATA_DIR="${APP_ROOT}/data/mysql"

docker run \
	-e MYSQL_ROOT_PASSWORD=ok \
	--name sqlserver \
	--network sql-network \
	--rm \
	-v $DATA_DIR:/var/lib/mysql \
	mysql