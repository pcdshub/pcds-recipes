#!/bin/bash
VERSION=3.3.14
git clone --depth 1 --branch $VERSION git@github.com:slac-lcls/lcls2.git patch-tmp
sed "s/VERSION/'$VERSION'/" setup.py > patch-tmp/psdaq/setup.py
pushd patch-tmp
git diff > ../setup.patch
popd
rm -rf patch-tmp
