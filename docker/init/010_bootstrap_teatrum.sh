#!/bin/bash

set -euo pipefail

echo "INIT: pripravuji uzivatele ${APP_USER} v PDB FREEPDB1"

sqlplus -s "system/${ORACLE_PASSWORD}@//localhost:1521/FREEPDB1" <<SQL
WHENEVER SQLERROR EXIT SQL.SQLCODE
ALTER USER ${APP_USER} QUOTA UNLIMITED ON USERS;
GRANT CREATE SESSION, CREATE TABLE, CREATE SEQUENCE, CREATE PROCEDURE, CREATE TRIGGER, CREATE TYPE, CREATE VIEW TO ${APP_USER};
EXIT
SQL

echo "INIT: nacitam schema a data TeatrumDB"

sqlplus -s "${APP_USER}/${APP_USER_PASSWORD}@//localhost:1521/FREEPDB1" <<'SQL'
WHENEVER SQLERROR EXIT SQL.SQLCODE
@/workspace/sql/01_schema.sql
@/workspace/sql/02_triggers.sql
@/workspace/sql/03_procedures.sql
@/workspace/sql/04_data.sql
EXIT
SQL

echo "INIT: TeatrumDB schema je pripravene"
