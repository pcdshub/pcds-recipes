#!/bin/bash
# Simple script for making sure the build works
mkdir -p conda-bld-tst
conda build $@ --output-folder conda-bld-tst -c "file://$(readlink -f conda-bld-tst)"
