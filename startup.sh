#!/usr/bin/env bash

echo "Server configs:"
cat server_config.py

#start server
python3 server.py >/tmp/memcached-lite.log 2>&1 &
sleep 1

#run some tests
python3 tests/test_basic_requirements.py

#begin CLI client
echo "Beginning CLI client"
python3 client_cli.py

sleep 1
kill %1
