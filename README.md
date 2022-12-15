# server-template

## Installation
This repository contains two systems; the database and the REST API.
As a database we use a containerized MySQL server (through Docker), the REST API can be run locally or containerized.

### Starting a MySQL Server 
First, we define a docker network to allow our server to be reachable from other docker containers:
```bash
docker network create sql-network
```

Then start the MySQL Server:
```bash
docker run -e MYSQL_ROOT_PASSWORD=ok --name sqlserver --network sql-network -p 3306:3306 -d mysql
```

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
