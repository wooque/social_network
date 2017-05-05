#!/usr/bin/env bash

if [ -z "$1" ]; then
    echo "No password supplied"
    exit 1
fi

psql -c "CREATE USER social_network WITH PASSWORD '$1'"
psql -c "ALTER ROLE social_network SET client_encoding TO 'utf8'"
psql -c "ALTER ROLE social_network SET default_transaction_isolation TO 'read committed'"
psql -c "ALTER ROLE social_network SET timezone TO 'UTC'"
psql -c "CREATE DATABASE social_network"
psql -c "GRANT ALL PRIVILEGES ON DATABASE social_network TO social_network"
