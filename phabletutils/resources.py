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

"""Resources for downloading and installing Ubuntu Touch."""

import downloads
import hashlib
import logging

log = logging.getLogger()


class File(object):
    """A file object that can be downloaded and flashed."""

    @property
    def uri(self):
        return self._uri

    @property
    def path(self):
        return self._path

    @property
    def verified(self):
        return self._verified

    @property
    def hash(self):
        return self._hash

    @property
    def hash_type(self):
        return self._hash_func

    @property
    def check(self):
        return self._check

    def __init__(self, file_uri, file_path, check=True, file_hash=None,
                 file_hash_func=hashlib.sha256):
        self._uri = file_uri
        self._path = file_path
        self._hash = file_hash
        self._hash_func = file_hash_func
        self._check = check
        if check and file_hash:
            self._verified = downloads.checksum_verify(file_path, file_hash,
                                                       file_hash_func)
            log.debug('%s verified: %s' % (file_path, self._verified))
        else:
            self._verified = False


class SignedFile(File):

    def sig_uri(self):
        return self._sig_uri

    @property
    def sig_path(self):
        return self._sig_path

    def __init__(self, file_uri, file_path, file_hash, sig_path, sig_uri,
                 check=True, file_hash_func=hashlib.sha256):
        super(SignedFile, self).__init__(
            file_uri, file_path, check, file_hash, file_hash_func)
        self._sig_path = sig_path
        self.sig_uri = sig_uri
