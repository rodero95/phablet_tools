# This program is free software: you can redistribute it and/or modify it
# under the terms of the the GNU General Public License version 3, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the applicable version of the GNU Lesser General Public
# License for more details.
#.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2013 Canonical, Ltd.

import logging
import os
import subprocess


log = logging.getLogger()


def download(uri, target_file):
    '''Downloads an artifact into target.'''
    log.info('Downloading %s' % uri)
    if uri.startswith('http://cdimage.ubuntu.com'):
        subprocess.check_call(['wget', '-c', uri, '-O', target_file])
    else:
        subprocess.check_call(['curl', '-C', '-', uri, '-o', target_file])


class DownloadManager(object):

    def __init__(self, base_uri, download_dir, artifact_list, offline=False):
        if not os.path.isdir(download_dir):
            raise RuntimeError('Directory %s does not exist or is not a '
                               'direcotry' % download_dir)
        self._base_uri = base_uri
        self._download_dir = download_dir
        self._artifact_list = artifact_list
        self._targets = {}
        self._offline = offline

    @property
    def files(self):
        return self._targets

    def _target_file(self, artifact):
        '''Constructs the path for the file to download.'''
        uri = '%s/%s' % (self._base_uri, artifact)
        target = os.path.join(self._download_dir, '%s' % (artifact))
        self._targets[artifact] = target
        return {'uri': uri, 'target_file': target}

    def download(self, validate=True):
        '''Downloads arget_uri.'''
        for artifact in self._artifact_list:
            target_file = self._target_file(artifact)
            if not self._offline:
                download(**target_file)
            if validate:
                md5file = '%s.md5sum' % artifact
                if not self._offline:
                    download(**self._target_file(md5file))
                self.validate(md5file)

    def validate(self, artifact):
        '''Validates downloaded files against md5sum.'''
        subprocess.check_call(['md5sum', '-c', '%s' % artifact],
                              cwd=self._download_dir)
