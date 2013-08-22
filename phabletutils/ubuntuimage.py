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

import json
import os.path

from phabletutils import downloads
from phabletutils import resources
from phabletutils import settings


def get_json_from_index(device, index):
    """Returns json index for device"""
    index -= 1
    json_index_uri = '%s/daily/%s/index.json' % \
        (settings.system_image_uri, device)
    json_content = downloads.get_content(json_index_uri)
    if not json_content:
        raise RuntimeError('%s cannot be retrieved' % json_index_uri)
    json_index = json.loads(json_content)
    json_dict = sorted([entry for entry in json_index['images']
                       if entry['type'] == "full"],
                       key=lambda entry: entry['version'])[index]
    return json_dict


def get_files(download_dir, uri, json):
    files = {}
    command_part = ''
    files = []
    for entry in sorted(json['files'], key=lambda entry: entry['order']):
        filename = entry['path'].split("/")[-1]
        signame = entry['signature'].split("/")[-1]
        f = resources.SignedFile(
            file_path=os.path.join(download_dir, filename),
            sig_path=os.path.join(download_dir, signame),
            file_uri='%s%s' % (uri, entry['path']),
            sig_uri='%s%s' % (uri, entry['signature']),
            file_hash=entry['checksum'])
        files.append(f)
        command_part += 'update %s %s\n' % (filename, signame)
    for keyring in ('image-master', 'image-signing'):
        filename = '%s.tar.xz' % keyring
        signame = '%s.asc' % filename
        f = resources.SignedFile(
            file_path=os.path.join(download_dir, filename),
            sig_path=os.path.join(download_dir, signame),
            file_uri='%s/gpg/%s' % (uri, filename),
            sig_uri='%s/gpg/%s.asc' % (uri, filename),
            file_hash=None)
        files.append(f)
    return files, command_part
