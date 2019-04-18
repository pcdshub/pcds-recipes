#!/usr/bin/env bash
anaconda auth --remove build --org pcds-tag
export ANACONDA_TOKEN=$(anaconda auth --create --name build --org pcds-tag --scopes api --max-age 1800)
./build.py --channel pcds-tag $@
