#!/bin/bash

set -euo pipefail

VERSION=$1

if [ -z "$VERSION" ];
then
    echo 'version number required'
    exit 1
fi

rm -rf R/
unzip -q R-$VERSION.zip -d R/
rm -r R/doc/manual/
chmod -R 755 bootstrap runtime.R R/
rm -f runtime.zip
zip -r -q runtime.zip runtime.R bootstrap R/
