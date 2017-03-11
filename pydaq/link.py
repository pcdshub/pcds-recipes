#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Build a package that is a symbolic link to the current correct daq python
package. This ensures we are always sync'd as we change daq releases. Using a
release for this package instead of using conda-develop lets us track module
dependencies.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *  # NOQA

import sys
import os
import subprocess
import re

def get_deps(shared_object):
    ldd_out = subprocess.check_output(["ldd", shared_object])
    deps = {}
    regex = re.compile(r'\t(.*) => (.*) \(0x')
    for line in ldd_out.splitlines():
        match = regex.match(line.decode('utf-8'))
        if match:
            deps[match.group(1)] = match.group(2)
    return deps

if __name__ == "__main__":
    try:
        hutch = os.environ["HUTCH"]
    except KeyError:
        raise RuntimeError("Set HUTCH environment variable before linking.")

    try:
        package = sys.argv[1]
    except IndexError:
        raise RuntimeError("Provide name of daq python package to link")

    hutch = hutch.lower()
    package = package + ".so"

    common_root = os.path.join("/reg/g/pcds/dist/pds", hutch)
    daq_root = os.path.join(common_root, "current/build")
    daq_py_dir = os.path.join(daq_root, "pdsapp/lib/x86_64-linux")
    ami_root = os.path.join(common_root, "ami-current/build")
    ami_py_dir = os.path.join(ami_root, "ami/lib/x86_64-linux")

    daq_so = os.path.join(daq_py_dir, package)
    ami_so = os.path.join(ami_py_dir, package)

    if os.path.exists(daq_so):
        target = daq_so
    elif os.path.exists(ami_so):
        target = ami_so
    else:
        raise RuntimeError("Could not find package {}".format(package))

    deps = get_deps(target)
    lib_dir = os.path.join(os.environ["PREFIX"], "lib")
    install = os.path.join(lib_dir, "python" + os.environ["PY_VER"],
                           "site-packages", package)
    links = [["ln", "-s", target, install]]

    for libname, path in deps.items():
        if common_root in path:
            links.append(["ln", "-s", path, os.path.join(lib_dir, libname)])

    for link in links:
        subprocess.check_output(link)
