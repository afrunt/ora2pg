#!/bin/sh

python3 /ora2pg_conf_initializer.py /etc/ora2pg.conf /etc-ora2pg/ora2pg.conf.dist

ora2pg-original $@