#!/usr/bin/env python
# Condensed version of nsls-ii's build scripts
import argparse
import shutil
import subprocess
import sys
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
from pathlib import Path
from socket import gethostname

import binstar_client

PACKAGES = ['epics-base', 'pcaspy', 'pyca', 'pydm', 'pyepics', 'pyqt',
            'mysqlclient']
PYTHON = ['3.6', '3.5']
NUMPY = ['1.14', '1.13', '1.12', '1.11']
BUILD_DIR = str(Path(__file__).parent / 'conda-bld')


def get_uploaded_files(client, channel):
    print('Checking uploaded files')
    files = set()
    for fl in client.show_channel('main', channel)['files']:
        files.add(fl['basename'])
    return files


def build_args(package, channel, py=None, np=None, dev=False):
    args = ['conda', 'build', package,
            '-c', channel, '-c', 'defaults', '-c', 'conda-forge',
            '--override', '--output-folder', BUILD_DIR,
            '--old-build-string']
    if py is not None:
        args.extend(['--python', py])
    if np is not None:
        args.extend(['--numpy', np])
    return args


def check_filename(package, channel, py=None, np=None):
    args = build_args(package, channel, py=py, np=np) + ['--output']
    print(' '.join(args))
    output = subprocess.check_output(args, universal_newlines=True).strip('\n')
    return output


def check_all(files, channel):
    to_build = {}
    index = 0
    pool = ThreadPool(processes=cpu_count()-1)
    results = []

    for package in PACKAGES:
        new_package = True
        for py in PYTHON:
            for np in NUMPY:
                args = (files, to_build, index, package, channel, py, np)
                if new_package:
                    # Do the first by itself or conda build may throw errors
                    res = pool.apply(func=_check_thread, args=args)
                    new_package = False
                else:
                    # Do the rest in parallel
                    res = pool.apply_async(func=_check_thread, args=args)
                    results.append(res)
                    index += 1

    for res in results:
        res.wait()

    return to_build


def _check_thread(files, to_build, index, package, channel, py, np):
    full_path = check_filename(package, channel, py=py, np=np)
    short_path = '/'.join(full_path.split('/')[-2:])
    if short_path not in files:
        files.add(short_path)
        to_build[index] = (package, channel, py, np, full_path)


def build(package, channel, py=None, np=None):
    print('Building {}'.format(package))
    args = build_args(package, channel, py=py, np=np)
    print(' '.join(args))
    subprocess.run(args, stdout=sys.stdout, stderr=subprocess.STDOUT)


def upload(client, channel, filename):
    print('Uploading {}'.format(filename))
    args = ['anaconda', '-t', client.token, 'upload', '-u', channel, filename]
    print(' '.join(args))
    subprocess.run(args, stdout=sys.stdout, stderr=subprocess.STDOUT)


def build_all():
    allowed_host = 'psbuild-rhel6'
    if gethostname() != allowed_host:
        print('You should be running this on {}!'.format(allowed_host))
        return
    print('Running build script')
    parser = argparse.ArgumentParser()
    parser.add_argument('--channel', action='store', required=True)
    parser.add_argument('--token', action='store', required=True)
    parser.add_argument('--no-build', action='store_true', required=False)
    args = parser.parse_args()

    channel = args.channel
    token = args.token

    client = binstar_client.Binstar(token=token)
    files = get_uploaded_files(client, channel)

    try:
        shutil.rmtree(BUILD_DIR)
    except Exception:
        pass
    build_path = Path(BUILD_DIR)
    build_path.mkdir()

    to_build = check_all(files, channel)
    built = []

    num = 0
    for _, (package, channel, py, np, full_path) in sorted(to_build.items()):
        if full_path not in built:
            num += 1
            built.append(full_path)
            if not args.no_build:
                build(package, channel, py=py, np=np)
                upload(client, channel, full_path)

    print('')
    if num == 0:
        print('Done. Built 0 packages.')
    else:
        print('Done. Built {} packages:'.format(num))
        for pkg in built:
            print(pkg)


if __name__ == '__main__':
    build_all()
