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
import stat
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
        module = sys.argv[1]
    except IndexError:
        raise RuntimeError("Provide name of daq python package to link")

    hutch = hutch.lower()
    package = module + ".so"

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
    ln = "ln -s {0} {1}\n"
    rm = "rm {}\n"
    links = ln.format(target, install)
    unlinks = rm.format(install)
    for libname, path in deps.items():
        if common_root in path:
            links += ln.format(path, os.path.join(lib_dir, libname))
            unlinks += rm.format(os.path.join(lib_dir, libname))

    paths = []
    for name in ("install", "uninstall"):
        paths.append(os.path.join(os.environ["PREFIX"],
                     "daq-links/{0}_{1}.sh".format(name, module)))

    for filename in paths:
        if not os.path.exists(filename):
            os.makedirs(os.path.dirname(filename))
        with open(filename, "w") as f:
            f.write(links)

        st = os.stat(filename)
        os.chmod(filename, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
