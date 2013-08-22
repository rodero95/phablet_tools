# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# Copyright (C) 2013 Canonical Ltd.
# Author: Sergio Schvezov <sergio.schvezov@canonical.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import configobj
import contextlib
import fcntl
import hashlib
import logging
import os
import requests
import subprocess

from xdg.BaseDirectory import xdg_config_home


log = logging.getLogger()


@contextlib.contextmanager
def flocked(lockfile):
    lockfile += '.lock'
    with open(lockfile, 'w') as f:
        log.debug('Aquiring lock for %s', lockfile)
        try:
            fcntl.lockf(f, fcntl.LOCK_EX)
            yield
        finally:
            log.debug('Releasing lock for %s', lockfile)
            fcntl.lockf(f, fcntl.LOCK_UN)


def setup_download_directory(download_dir):
    '''
    Tries to create the download directory from XDG_DOWNLOAD_DIR or sets
    an alternative one.

    Returns path to directory
    '''
    log.info('Download directory set to %s' % download_dir)
    if not os.path.exists(download_dir):
        log.info('Creating %s' % download_dir)
        try:
            os.makedirs(download_dir)
        except OSError as e:
            if e.errno == 17:
                pass
            else:
                raise e


def get_full_path(subdir):
    try:
        userdirs_file = os.path.join(xdg_config_home, 'user-dirs.dirs')
        userdirs_config = configobj.ConfigObj(userdirs_file, encoding='utf-8')
        userdirs_download = os.path.expandvars(
            userdirs_config['XDG_DOWNLOAD_DIR'])
        download_dir = userdirs_download
    except KeyError:
        download_dir = os.path.expandvars('$HOME')
        log.warning('XDG_DOWNLOAD_DIR could not be read')
    directory = os.path.join(download_dir, subdir)
    setup_download_directory(directory)
    return directory


def checksum_verify(file_path, file_hash, sum_method=hashlib.sha256):
    '''Returns the checksum for a file with a specified algorightm.'''
    file_sum = sum_method()
    log.debug('Verifying file: %s against: %s' % (file_path, file_hash))
    if not os.path.exists(file_path):
        log.debug('File %s not found' % file_path)
        return False
    with open(file_path, 'rb') as f:
        for file_chunk in iter(
                lambda: f.read(file_sum.block_size * 128), b''):
            file_sum.update(file_chunk)
    if file_hash == file_sum.hexdigest():
        return True
    else:
        log.debug('Calculated sum mismatch calculated %s != %s' %
                  (file_sum.hexdigest(), file_hash))
    return False


def _download(uri, path):
    if uri.startswith('http://cdimage.ubuntu.com') or \
       uri.startswith('https://system-image.ubuntu.com'):
        subprocess.check_call(['wget',
                               '-c',
                               uri,
                               '-O',
                               path])
    else:
        subprocess.check_call(['curl',
                               '-L',
                               '-C',
                               '-',
                               uri,
                               '-o',
                               path])


def download_sig(artifact):
    '''Downloads an artifact into target.'''
    log.info('Downloading %s to %s' % (artifact.uri, artifact.path))
    with flocked(artifact._sig_path):
        _download(artifact.sig_uri, artifact.sig_path)


def download(artifact):
    '''Downloads an artifact into target.'''
    log.info('Downloading %s to %s' % (artifact.uri, artifact.path))
    with flocked(artifact._path):
        _download(artifact.uri, artifact.path)


def get_content(uri):
    '''Fetches the SHA256 sum file from cdimage.'''
    content_request = requests.get(uri)
    if content_request.status_code != 200:
        return None
    else:
        return content_request.content
