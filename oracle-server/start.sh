#!/bin/bash

docker run --name shopdb -h kdc.h4vms.com -d -p 51521:1521 -p 55500:5500 -e ORACLE_PWD=orcl -v /home/h4vm/oracle-home/oracle-client/shop/oracle2/oradata:/opt/oracle/oradata -v /home/h4vm/oracle-home/oracle-client/shop/oracle2/scripts/setup:/opt/oracle/scripts/setup -v /home/h4vm/oracle-home/oracle-client/shop/oracle2/scripts/startup:/opt/oracle/scripts/startup -v /home/h4vm/oracle-home/oracle-client/shop/kerberos:/var/kerberos oracle/database:18.4.0-
