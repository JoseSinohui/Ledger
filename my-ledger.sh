#!/bin/bash
./ledger.py  --price-db prices_db \
-f index.ledger "$@"
