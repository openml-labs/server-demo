#/bin/bash



APP_ROOT="$(dirname "$(dirname "$(readlink -fm "$0")")")"
SRC_PATH="${APP_ROOT}/src"


docker run \
	--network sql-network\
	--rm \
	-p 8000:8000 \
	--name apiserver \
	-v $SRC_PATH:/app \
	ai4eu_server_demo \
	--rebuild-db always