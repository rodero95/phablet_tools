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

"""Unit tests for phabletutils.environment."""

import json
import shutil
import tempfile

from os import path
from phabletutils import community
from testtools import TestCase
from testtools.matchers import Equals
from testtools.matchers import Is


class TestCommunityManifestLoad(TestCase):

    def setUp(self):
        super(TestCommunityManifestLoad, self).setUp()
        self.device_dir = tempfile.mkdtemp()

    def tearDown(self):
        super(TestCommunityManifestLoad, self).tearDown()
        shutil.rmtree(self.device_dir)

    def testSimpleDeviceManifest(self):
        # given
        manifest = {'device': 'http://somelocation.com/device.zip'}
        with open(path.join(self.device_dir, 'manifest.json'), 'w') as f:
                f.write(json.dumps(manifest))
        # when
        loaded_manifest = community.load_manifest(self.device_dir)
        # then
        self.assertThat(loaded_manifest['device'], Equals(manifest['device']))
        self.assertThat(loaded_manifest['ubuntu'], Is(None))
        self.assertThat(loaded_manifest['revision'], Is(None))
        self.assertThat(loaded_manifest['storage'], Equals('/sdcard/'))

    def testSimpleDeviceAndUbuntuManifest(self):
        # given
        manifest = {'device': 'http://somelocation.com/device.zip',
                    'ubuntu': 'http://somelocation.com/ubuntu.zip'}
        with open(path.join(self.device_dir, 'manifest.json'), 'w') as f:
                f.write(json.dumps(manifest))
        # when
        loaded_manifest = community.load_manifest(self.device_dir)
        # then
        self.assertThat(loaded_manifest['device'], Equals(manifest['device']))
        self.assertThat(loaded_manifest['ubuntu'], Equals(manifest['ubuntu']))
        self.assertThat(loaded_manifest['revision'], Is(None))
        self.assertThat(loaded_manifest['storage'], Equals('/sdcard/'))

    def testSimpleDeviceAndUbuntuRevisionManifest(self):
        # given
        manifest = {'device': 'http://somelocation.com/device.zip',
                    'ubuntu': 'http://somelocation.com/ubuntu.zip',
                    'revision': 'unstable'}
        with open(path.join(self.device_dir, 'manifest.json'), 'w') as f:
                f.write(json.dumps(manifest))
        # when
        loaded_manifest = community.load_manifest(self.device_dir)
        # then
        self.assertThat(loaded_manifest['device'], Equals(manifest['device']))
        self.assertThat(loaded_manifest['ubuntu'], Equals(manifest['ubuntu']))
        self.assertThat(loaded_manifest['revision'],
                        Equals(manifest['revision']))
        self.assertThat(loaded_manifest['storage'], Equals('/sdcard/'))

    def testSimpleDeviceAndUbuntuRevisionStorageManifest(self):
        # given
        manifest = {'device': 'http://somelocation.com/device.zip',
                    'ubuntu': 'http://somelocation.com/ubuntu.zip',
                    'storage': '/emmc/',
                    'revision': 'unstable'}
        with open(path.join(self.device_dir, 'manifest.json'), 'w') as f:
                f.write(json.dumps(manifest))
        # when
        loaded_manifest = community.load_manifest(self.device_dir)
        # then
        self.assertThat(loaded_manifest['device'], Equals(manifest['device']))
        self.assertThat(loaded_manifest['ubuntu'], Equals(manifest['ubuntu']))
        self.assertThat(loaded_manifest['revision'],
                        Equals(manifest['revision']))
        self.assertThat(loaded_manifest['storage'],
                        Equals(manifest['storage']))


class TestCommunityFiles(TestCase):

    def setUp(self):
        super(TestCommunityFiles, self).setUp()
        self.download_dir = '/downloads'
        self.series = 'saucy'

    def tearDown(self):
        super(TestCommunityFiles, self).tearDown()

    def testSimpleDeviceAndUbuntu(self):
        # given
        manifest = {'device': 'http://somelocation.com/device.zip',
                    'ubuntu': 'http://somelocation.com/ubuntu.zip'}
        # when
        files = community.get_files(manifest, self.download_dir, self.series)
        #then
        self.assertThat(files['device'].uri, Equals(manifest['device']))
        self.assertThat(files['device'].hash, Is(None))
        self.assertThat(files['device'].verified, Is(False))
        self.assertThat(files['device'].path,
                        Equals(path.join(self.download_dir,
                               path.basename(manifest['device']))))
        self.assertThat(files['ubuntu'].uri, Equals(manifest['ubuntu']))
        self.assertThat(files['ubuntu'].hash, Is(None))
        self.assertThat(files['ubuntu'].verified, Is(False))
        self.assertThat(files['ubuntu'].path,
                        Equals(path.join(self.download_dir,
                               path.basename(manifest['ubuntu']))))
