# LICENSE UPL 1.0
#
# Copyright (c) 2014, 2020, Oracle and/or its affiliates.
#
# Container image template for Oracle Instant Client
#
# HOW TO BUILD THIS IMAGE
# -----------------------
#
# Run:
#      $ docker build --pull -t oracle/instantclient:18 .
#
#
FROM oraclelinux:7-slim

ARG release=18
ARG update=5

COPY ./shop/ /shop/

#RUN mv /usr/bin/systemctl /usr/bin/systemctl.old
#RUN curl https://raw.githubusercontent.com/gdraheim/docker-systemctl-replacement/master/files/docker/systemctl.py > /usr/bin/systemctl
#RUN chmod +x /usr/bin/systemctl

RUN yum -y install krb5-workstation

RUN  yum -y install oracle-release-el7 && yum-config-manager --enable ol7_oracle_instantclient && \
     yum -y install oracle-instantclient${release}.${update}-basic oracle-instantclient${release}.${update}-devel oracle-instantclient${release}.${update}-sqlplus && yum -y install python3 && yum -y install vim net-tools && \
     rm -rf /var/cache/yum && \
     echo /usr/lib/oracle/${release}.${update}/client64/lib > /etc/ld.so.conf.d/oracle-instantclient${release}.${update}.conf && \
     ldconfig

RUN rm -rf /shop/venv && python3 -m venv /shop/venv && source /shop/venv/bin/activate  && pip install --upgrade pip && pip install gevent flask flask_sqlalchemy flask_migrate flask_socketio flask_jwt_extended redis cx_Oracle 

RUN cd /shop/ && source venv/bin/activate 
#&& python3 -m flask db init && python3 -m flask db migrate && python3 -m flask db upgrade

ENV PATH=$PATH:/usr/lib/oracle/${release}.${update}/client64/bin

CMD ["python3" "/shop/shop.py"]
