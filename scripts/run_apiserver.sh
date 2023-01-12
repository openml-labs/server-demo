#/bin/bash

docker run \
	--network sql-network\
	--rm \
	-p 8000:8000 \
	--name apiserver \
	-v /ABSOLUTE/PATH/TO/SRC:/app \
	ai4eu_server_demo \
	--rebuild-db always