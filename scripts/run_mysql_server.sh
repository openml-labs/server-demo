#/bin/bash

APP_ROOT="$(dirname "$(dirname "$(readlink -fm "$0")")")"
DATA_DIR="${APP_ROOT}/data/mysql"

docker run \
	-e MYSQL_ROOT_PASSWORD=ok \
	--name sqlserver \
	--network sql-network \
	--rm \
	-v $DATA_DIR:/var/lib/mysql \
	mysql