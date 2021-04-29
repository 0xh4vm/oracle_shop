#!/bin/bash

docker run --name clientdb -h kdc2.h4vms.com  -d -p 41521:1521 -p 45500:5500 -e ORACLE_PWD=orcl oracle/database:18.4.0-
