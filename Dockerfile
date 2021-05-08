FROM oraclelinux:7-slim

# https://github.com/bumpx/oracle-instantclient/raw/master/oracle-instantclient19.6-basic-19.6.0.0.0-1.x86_64.rpm
ADD dependencies/oracle-instantclient19.6-basic-19.6.0.0.0-1.x86_64.rpm /tmp/

# https://github.com/bumpx/oracle-instantclient/raw/master/oracle-instantclient19.6-devel-19.6.0.0.0-1.x86_64.rpm
ADD dependencies/oracle-instantclient19.6-devel-19.6.0.0.0-1.x86_64.rpm /tmp/

# https://github.com/bumpx/oracle-instantclient/raw/master/oracle-instantclient19.6-sqlplus-19.6.0.0.0-1.x86_64.rpm
ADD dependencies/oracle-instantclient19.6-sqlplus-19.6.0.0.0-1.x86_64.rpm /tmp/

# https://cpan.metacpan.org/authors/id/Z/ZA/ZARQUON/DBD-Oracle-1.76.tar.gz
ADD dependencies/DBD-Oracle-1.76.tar.gz /tmp/

# https://github.com/darold/ora2pg/archive/refs/tags/v21.1.tar.gz
ADD dependencies/v21.1.tar.gz /tmp/

RUN echo "Building..." \
    && yum update -y \
    && yum upgrade -y \
    && yum install -y python3 make gcc gzip perl-DBI perl-CPAN tar perl-DBD-Pg postgresql-devel

ENV ORACLE_HOME=/usr/lib/oracle/19.6/client64 \
    TNS_ADMIN=/usr/lib/oracle/19.6/client64/network/admin \
    LD_LIBRARY_PATH=/usr/lib/oracle/19.6/client64/lib \
    PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/lib/oracle/19.6/client64/bin

RUN echo "Installing dependencies..." \
    && yum -y localinstall /tmp/oracle-instantclient*.rpm \
    && echo /usr/lib/oracle/19.6/client64/lib > /etc/ld.so.conf.d/oracle-instantclient19.6.conf \
    && ldconfig \
    && mkdir /usr/lib/oracle/19.6/client64/network/admin -p \
    && cd /tmp && mv /tmp/DBD-Ora* /tmp/DBD-Oracle \
    && cd /tmp/DBD-Oracle && perl Makefile.PL -l && make && make install \
    && mkdir /data \
    && cd /tmp  && mv /tmp/ora2pg* /tmp/ora2pg \
    && cd /tmp/ora2pg && perl Makefile.PL && make && make install \
    && mkdir /etc-ora2pg \
    && cp /etc/ora2pg/* /etc-ora2pg/ \
    && rm -rf /tmp/* && rm -rf /var/cache/yum \
    && mv /usr/local/bin/ora2pg /usr/local/bin/ora2pg-original

ADD ora2pg_conf_initializer.py /
ADD ora2pg.sh /usr/local/bin/ora2pg

RUN chmod +x /usr/local/bin/ora2pg

CMD ora2pg


