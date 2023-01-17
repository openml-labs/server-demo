#/bin/bash

docker run \
	-it --rm \
	--network sql-network \
	mysql mysql \
	-hsqlserver \
	-uroot -pok