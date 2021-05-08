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

ENV \
   ORACLE_HOME="/usr/lib/oracle/19.6/client64" \
   ORACLE_DSN="dbi:Oracle:host=mydb.mydom.fr;sid=SIDNAME;port=1521" \
   ORACLE_USER="system" \
   ORACLE_PWD="manager" \
   USER_GRANTS="0" \
   DEBUG="0" \
   EXPORT_SCHEMA="0" \
   CREATE_SCHEMA="1" \
   COMPILE_SCHEMA="1" \
   NO_FUNCTION_METADATA="0" \
   TYPE="TABLE" \
   DISABLE_COMMENT="0" \
   NO_VIEW_ORDERING="0" \
   EXTERNAL_TO_FDW="1" \
   TRUNCATE_TABLE="0" \
   USE_TABLESPACE="0" \
   REORDERING_COLUMNS="0" \
   CONTEXT_AS_TRGM="0" \
   FTS_INDEX_ONLY="1" \
   USE_UNACCENT="0" \
   USE_LOWER_UNACCENT="0" \
   DATADIFF="0" \
   DATADIFF_UPDATE_BY_PKEY="0" \
   DATADIFF_DEL_SUFFIX="_del" \
   DATADIFF_UPD_SUFFIX="_upd" \
   DATADIFF_INS_SUFFIX="_ins" \
   DATADIFF_WORK_MEM="256 MB" \
   DATADIFF_TEMP_BUFFERS="512 MB" \
   KEEP_PKEY_NAMES="0" \
   PKEY_IN_CREATE="0" \
   FKEY_ADD_UPDATE="never" \
   FKEY_DEFERRABLE="0" \
   DEFER_FKEY="0" \
   DROP_FKEY="0" \
   DISABLE_SEQUENCE="0" \
   DISABLE_TRIGGERS="0" \
   PRESERVE_CASE="0" \
   INDEXES_RENAMING="0" \
   USE_INDEX_OPCLASS="0" \
   PREFIX_PARTITION="0" \
   PREFIX_SUB_PARTITION="1" \
   DISABLE_PARTITION="0" \
   WITH_OID="0" \
   ORA_RESERVED_WORDS="audit,comment,references" \
   USE_RESERVED_WORDS="0" \
   DISABLE_UNLOGGED="0" \
   OUTPUT="output.sql" \
   BZIP="BZIP2" \
   FILE_PER_CONSTRAINT="0" \
   FILE_PER_INDEX="0" \
   FILE_PER_FKEYS="0" \
   FILE_PER_TABLE="0" \
   FILE_PER_FUNCTION="0" \
   STOP_ON_ERROR="1" \
   COPY_FREEZE="0" \
   CREATE_OR_REPLACE="1" \
   PG_NUMERIC_TYPE="1" \
   PG_INTEGER_TYPE="1" \
   DEFAULT_NUMERIC="bigint" \
   ENABLE_MICROSECOND="1" \
   TO_NUMBER_CONVERSION="numeric" \
   GEN_USER_PWD="0" \
   FORCE_OWNER="0" \
   FORCE_SECURITY_INVOKER="0" \
   DATA_LIMIT="10000" \
   NOESCAPE="0" \
   TRANSACTION="serializable" \
   STANDARD_CONFORMING_STRINGS="1" \
   USE_LOB_LOCATOR="1" \
   LOB_CHUNK_SIZE="512000" \
   XML_PRETTY="0" \
   LOG_ON_ERROR="0" \
   TRIM_TYPE="BOTH" \
   INTERNAL_DATE_MAX="49" \
   FUNCTION_CHECK="1" \
   ENABLE_BLOB_EXPORT="1" \
   DATA_EXPORT_ORDER="name" \
   PSQL_RELATIVE_PATH="0" \
   JOBS="1" \
   ORACLE_COPIES="1" \
   PARALLEL_TABLES="1" \
   DEFAULT_PARALLELISM_DEGREE="0" \
   PARALLEL_MIN_ROWS="100000" \
   DROP_INDEXES="0" \
   SYNCHRONOUS_COMMIT="0" \
   EXPORT_INVALID="0" \
   PLSQL_PGSQL="1" \
   NULL_EQUAL_EMPTY="0" \
   EMPTY_LOB_NULL="1" \
   PACKAGE_AS_SCHEMA="1" \
   REWRITE_OUTER_JOIN="1" \
   FUNCTION_STABLE="1" \
   COMMENT_COMMIT_ROLLBACK="0" \
   COMMENT_SAVEPOINT="0" \
   USE_ORAFCE="0" \
   AUTONOMOUS_TRANSACTION="1" \
   ESTIMATE_COST="0" \
   COST_UNIT_VALUE="5" \
   DUMP_AS_HTML="0" \
   TOP_MAX="10" \
   HUMAN_DAYS_LIMIT="5" \
   PG_VERSION="12" \
   BITMAP_AS_GIN="1" \
   PG_BACKGROUND="0" \
   PG_SUPPORTS_SUBSTR="1" \
   AUTODETECT_SPATIAL_TYPE="1" \
   CONVERT_SRID="1" \
   DEFAULT_SRID="4326" \
   GEOMETRY_EXTRACT_TYPE="INTERNAL" \
   FDW_SERVER="orcl" \
   MYSQL_PIPES_AS_CONCAT="0" \
   MYSQL_INTERNAL_EXTRACT_FORMAT="0"

ADD ora2pg_conf_initializer.py /
ADD ora2pg.sh /usr/local/bin/ora2pg

RUN chmod +x /usr/local/bin/ora2pg

CMD ora2pg


