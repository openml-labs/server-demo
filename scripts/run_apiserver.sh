#/bin/bash

SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)"
APP_ROOT="$(dirname $SCRIPT_PATH)"
SRC_PATH="${APP_ROOT}/src"

docker run \
	--network sql-network\
	--rm \
	-p 8000:8000 \
	--name apiserver \
	-v $SRC_PATH:/app \
	ai4eu_server_demo \
	--rebuild-db always \
	--populate-datasets openml huggingface \
	--populate-publications example \
	--url-prefix ""