#/bin/bash

docker run \
	--network sql-network\
	-it --rm \
	-p 8000:8000 \
	--name apiserver \
	ai4eu_server_demo