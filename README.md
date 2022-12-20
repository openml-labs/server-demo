# FastAPI + Database (MySQL) Server Demo

This repository contains an example of how to provide a REST API built with [FastAPI](https://fastapi.tiangolo.com/)
that interacts with a database ([MySQL](https://hub.docker.com/_/mysql)) and [OpenML's REST API](https://www.openml.org/apis).
Both the database and the REST API are run from docker in separate containers.

## Installation
This repository contains two systems; the database and the REST API.
As a database we use a containerized MySQL server (through Docker), the REST API can be run locally or containerized.
Information on how to install Docker is found in [their documentation](https://docs.docker.com/desktop/).

### Starting a MySQL Server 
We use the default [MySQL Docker image](https://hub.docker.com/_/mysql).
By default, the database is stored within the docker container and will thus be deleted when the container is removed.
Instructions on using a persistent storage can be found at the end of this section.

First, we define a docker network to allow our server to be reachable from other docker containers:

```bash
docker network create sql-network
```

Then, start the MySQL Server:
```bash
docker run -e MYSQL_ROOT_PASSWORD=ok --name sqlserver --network sql-network -p 3306:3306 -d mysql
```

That's all! You should be able to connect to the server now, though no database is present yet:

```bash
docker run -it --network sql-network --rm mysql mysql -hsqlserver -uroot -pok
```

```bash
mysql> SHOW DATABASES;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| sys                |
+--------------------+
4 rows in set (0.03 sec)
```

#### Persistent Storage
The data is persistent when simply stopping and restarting the server:

```bash
docker stop demodb
docker start demodb
```

However, all data is lost when the container is deleted.
To ensure data can persist even if the container is deleted, allow the Docker container to write to a directory on the host machine. 
To do that, mount a volume by adding `-v /ABSOLUTE/PATH/TO/HOST/DIR:/var/lib/mysql` to the docker command that starts the server 
(it's also possible to create a docker volume ([docs](https://docs.docker.com/engine/reference/commandline/run/#mount-volume--v---read-only))).
If you want to use a path within this repository directory, we recommend naming the directory `data` since then it will automatically be ignored by git.
For more information, see "Where to Store Data" in the linked documentation.

### Starting the REST API

#### Local
Set up a Python environment and install the dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```
Start the server:
```bash
uvicorn src.main:app --reload
```

#### Containerized

