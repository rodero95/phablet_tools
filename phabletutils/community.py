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

from __future__ import print_function

import json
import hashlib
import logging
import os
import os.path
import subprocess

from phabletutils import cdimage
from phabletutils import downloads
from phabletutils import resources
from phabletutils import license
from phabletutils import settings

log = logging.getLogger()
branch_template = 'lp:~{0}-image-dev/phablet-image-info/{0}'
base_dir = os.path.join(settings.download_dir, 'community')

license_template = '''This community project has the following license:

{0}
'''


def branch_project(device):
    branch = branch_template.format(device.replace('_', '-'))
    log.info('Obtaining project branch from %s' % branch)
    download_dir = downloads.get_full_path(os.path.join(base_dir, device))
    target = os.path.join(download_dir, 'config')
    if os.path.exists(target):
        subprocess.check_call(['bzr', 'update'], cwd=target)
    else:
        subprocess.check_call(
            ['bzr', 'checkout', '--lightweight', branch, target])
    log.info('Target config retrieved to %s' % target)
    # Best time to do this is right after retrieving the config
    ensure_license_accept(download_dir, os.path.join(target, 'license'))
    return target


def ensure_license_accept(download_dir, license_file):
    if not os.path.exists(license_file):
        raise EnvironmentError('Project does not offer a license file')
    accept_path = os.path.join(download_dir, '.license_accept')
    with open(license_file, 'r') as f:
        device_license = f.read()
    device_license = 'LICENSE TEXT NOT PROVIDED BY PORT MAINTAINER' \
        if not device_license else device_license
    message = license_template.format(device_license)
    if not license.has_accepted(accept_path) and \
       not license.query(message, accept_path):
        raise RuntimeError('License not accepted.')


def load_manifest(directory):
    manifest_file = os.path.join(directory, 'manifest.json')
    if not os.path.exists(manifest_file):
        raise RuntimeError('Cannot locate %s' % manifest_file)
    with open(manifest_file) as f:
        manifest_dict = json.load(f)
    if 'device' not in manifest_dict:
        raise EnvironmentError('device entry required in manifest')
    if 'revision' not in manifest_dict:
        manifest_dict['revision'] = None
    if 'storage' not in manifest_dict:
        manifest_dict['storage'] = '/sdcard/'
    if 'ubuntu' not in manifest_dict:
        manifest_dict['ubuntu'] = None
    log.debug(json.dumps(manifest_dict))
    return manifest_dict


def get_download_dir(device, revision=None):
    download_dir = os.path.join(settings.download_dir, 'community', device)
    if revision:
        download_dir = os.path.join(download_dir, revision)
    return downloads.get_full_path(download_dir)


def get_files(manifest_dict, download_dir, series):
    files = {}
    for key in ('device', 'ubuntu'):
        if isinstance(manifest_dict[key], dict):
            item = manifest_dict[key]
            hash_type = item['hash_func'] if 'hash_func' in item else None
            log.debug('%s has config uri: %s' % (key, item['uri']))
            files[key] = resources.File(
                file_path=os.path.join(download_dir, '%s.zip' % key),
                file_uri=item['uri'],
                file_hash=item['hash'] if 'hash' in item else None,
                file_hash_func=get_hash_func(hash_type) if hash_type else None)
        elif isinstance(manifest_dict[key], str) or \
                isinstance(manifest_dict[key], unicode):
            log.debug('%s has config uri: %s' % (key, manifest_dict[key]))
            files[key] = resources.File(
                file_path=os.path.join(download_dir, '%s.zip' % key),
                file_uri=manifest_dict[key],
                file_hash=None)
        log.debug('%s is type %s' % (key, type(manifest_dict[key])))
    if not manifest_dict['ubuntu']:
        log.warning('Using Ubuntu Touch current build for ubuntu image')
        files['ubuntu'] = cdimage.get_file(file_key='ubuntu_zip',
                                           series=series,
                                           download_dir=download_dir)
    return files


def get_hash_func(hash_type):
    return {
        'md5': hashlib.md5,
        'sha256': hashlib.sha256,
        }.get(hash_type, None)
