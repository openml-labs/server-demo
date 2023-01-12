#/bin/bash

docker run \
	-e MYSQL_ROOT_PASSWORD=ok \
	--name sqlserver \
	--network sql-network \
	--rm \
	-v /your/absolute/path/to/the/data:/var/lib/mysql \
	mysql