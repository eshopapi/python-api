#!/bin/bash

# Maybe use `poe docs` instead.

echo "Deleting old reference"
[ -d "docs/reference" ] && rm -rf "docs/reference"

echo "Building new reference using pdoc3"
pdoc3 --html -o "docs/" shopapi
mv "docs/shopapi" "docs/reference"
