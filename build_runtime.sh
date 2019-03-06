#!/bin/bash

set -euo pipefail

rm -rf R/
unzip -q R.zip -d R/
rm -r R/doc/manual/
chmod -R 755 bootstrap runtime.R R/
rm -f runtime.zip
zip -r -q runtime.zip runtime.R bootstrap R/
