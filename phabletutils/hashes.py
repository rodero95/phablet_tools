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

import logging
import os.path

from phabletutils import downloads

log = logging.getLogger()


def hash2dict(hash_file_content):
    '''Returns a dictionary with the sha256 sums for all files.'''
    if not hash_file_content:
        log.debug('hash file is empty')
        return None
    hash_list = filter((lambda x: len(x) is not 0),
                       hash_file_content.split('\n'))
    hash_list = [h.split() for h in hash_list]
    hash_dict = {}
    for hash_entry in hash_list:
        if hash_entry[1][0] == '*':
            hash_entry[1] = hash_entry[1][1:]
        hash_dict[hash_entry[1]] = hash_entry[0]
    return hash_dict


def load_hash(uri, artifact, download_dir=None):
    if download_dir:
        hash_path = os.path.join(download_dir, artifact)
    else:
        hash_path = None
    hashes = {}
    if hash_path and os.path.exists(hash_path):
        with open(hash_path, 'r') as f:
            file_hash_content = f.read()
        hashes = hash2dict(file_hash_content)
    if uri:
        uri = '%s/%s' % (uri, artifact)
        hash_content = downloads.get_content(uri)
        if not hash_content:
            raise RuntimeError('%s cannot be downloaded' % uri)
        hashes.update(hash2dict(hash_content))
        if hash_path:
            log.debug('Storing hash to %s' % hash_path)
            with downloads.flocked(hash_path):
                with open(hash_path, 'w') as f:
                    for key in hashes:
                        f.write('%s %s\n' % (hashes[key], key))
    if hashes:
        return hashes
    else:
        raise RuntimeError('%s cannot be obtained for verifiaction' % artifact)
