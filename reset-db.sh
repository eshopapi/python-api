#!/bin/bash

rm db.sqlite3*
rm -rf migrations/
poe db-init-migrations
poe db-init
