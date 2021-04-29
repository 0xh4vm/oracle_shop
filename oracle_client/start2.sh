#!/bin/bash

docker run --rm -p 31521:1521 -h kdc3.h4vms.com -it oracle/instantclient:18-python /bin/bash
