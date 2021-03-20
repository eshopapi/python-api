#!/bin/bash

rm db.sqlite3*
./drop-public.sh
rm -rf migrations/
poe db-init-migrations
poe db-init
