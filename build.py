#!/usr/bin/env python
# Condensed version of nsls-ii's build scripts
import argparse
import logging
import os
import shutil
import subprocess
import sys
from logging.handlers import RotatingFileHandler
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
from pathlib import Path
from socket import gethostname

import binstar_client

logger = logging.getLogger('pcds_recipes.build')

PACKAGES = [pkg for pkg in os.listdir()
            if Path(pkg).is_dir() and (Path(pkg) / 'meta.yaml').exists()]

PYTHON = ['3.7', '3.6']
NUMPY = ['1.16', '1.15']
BUILD_DIR = str(Path(__file__).parent / 'conda-bld')


def get_uploaded_files(client, channel):
    logger.info('Checking uploaded files')
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
    return run_and_log(args).strip('\n')


def check_all(files, channel, packages=None):
    packages = packages or PACKAGES
    to_build = {}
    index = 0
    pool = ThreadPool(processes=cpu_count()-1)
    results = []

    for package in packages:
        new_package = True
        for py in PYTHON:
            for np in NUMPY:
                args = (files, to_build, index, package, channel, py, np)
                if new_package:
                    # Do the first by itself or conda build may throw errors
                    pool.apply(func=_check_thread, args=args)
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
    logger.info('Building {}'.format(package))
    args = build_args(package, channel, py=py, np=np)
    run_and_log(args)


def upload(client, channel, filename):
    logger.info('Uploading {}'.format(filename))
    args = ['anaconda', '-t', client.token, 'upload', '-u', channel, filename]
    run_and_log(args)


def run_and_log(args):
    logger.info(' '.join(args))
    txt = ''
    process = subprocess.Popen(args,
                               stdout=subprocess.PIPE,
                               universal_newlines=True)
    with process.stdout as pipe:
        for line in iter(pipe.readline, ''):
            logger.info(line.strip('\n'))
            txt += line
    return txt


def configure_logger():
    log_dir = Path(os.path.dirname(__file__)) / 'logs'
    log_file = log_dir / 'build.log'

    if not log_dir.exists():
        log_dir.mkdir(parents=True)
    if log_file.exists():
        do_rollover = True
    else:
        do_rollover = False

    stream_handler = logging.StreamHandler()
    file_handler = RotatingFileHandler(str(log_file),
                                       backupCount=5,
                                       encoding=None,
                                       delay=0)
    if do_rollover:
        file_handler.doRollover()
    formatter = logging.Formatter(fmt=('%(asctime)s.%(msecs)03d '
                                       '%(name)-18s '
                                       '%(levelname)-8s '
                                       '%(threadName)-10s '
                                       '%(message)s'),
                                  datefmt='%H:%M:%S')

    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)



def build_all():
    logger.info('Running build script')
    parser = argparse.ArgumentParser()
    parser.add_argument('packages', nargs='*')
    parser.add_argument('--channel', action='store', required=True)
    parser.add_argument('--no-build', action='store_true', required=False)
    parser.add_argument('--no-upload', action='store_true', required=False)
    parser.add_argument('--del-old-builds', action='store_true', required=False)
    parser.add_argument('--token', action='store')
    args = parser.parse_args()

    channel = args.channel

    # Grab token from environment variable if not specified
    if not args.token and not args.no_upload:
        token = os.getenv('ANACONDA_TOKEN')
        if not token:
            raise ValueError("Token must be provided using `--token` or in "
                             "environment variable 'ANACONDA_TOKEN', or you "
                             "can specify --no-upload.")
    else:
        token = args.token

    if token:
        client = binstar_client.Binstar(token=token)
        files = get_uploaded_files(client, channel)
    else:
        files = set()

    if args.del_old_builds:
        try:
            shutil.rmtree(BUILD_DIR)
        except Exception:
            pass
    build_path = Path(BUILD_DIR)
    if not build_path.exists():
        build_path.mkdir()

    to_build = check_all(files, channel, packages=args.packages)
    built = []

    num = 0
    for _, (package, channel, py, np, full_path) in sorted(to_build.items()):
        if full_path not in built:
            num += 1
            built.append(full_path)
            if not args.no_build:
                build(package, channel, py=py, np=np)
                if not args.no_upload:
                    upload(client, channel, full_path)

    if num == 0:
        logger.info('Done. Built 0 packages.')
    else:
        logger.info('Done. Built {} packages:'.format(num))
        for pkg in built:
            logger.info(pkg)


if __name__ == '__main__':
    configure_logger()
    build_all()
