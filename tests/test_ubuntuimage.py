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

from mock import patch
from phabletutils import ubuntuimage
from testtools import TestCase
from testtools.matchers import Equals
from testtools.matchers import HasLength


@patch('phabletutils.downloads.get_content')
class TestUbuntuImage(TestCase):

    def setUp(self):
        super(TestUbuntuImage, self).setUp()
        self.device = 'mako'
        with open('tests/index.json', 'r') as f:
            self.json_content = f.read()

    def testGetLatestIndex(self, get_content_mock):
        # given
        get_content_mock.return_value = self.json_content
        # when
        json_dict = ubuntuimage.get_json_from_index(self.device, 0)
        # then
        self.assertThat(json_dict['version'], Equals(20130808))
        self.assertThat(json_dict['description'], Equals('20130807'))
        self.assertThat(json_dict['type'], Equals('full'))
        self.assertThat(json_dict['files'], HasLength(3))

    def testGetPreviousIndex(self, get_content_mock):
        # given
        get_content_mock.return_value = self.json_content
        # when
        json_dict = ubuntuimage.get_json_from_index(self.device, -1)
        # then
        self.assertThat(json_dict['version'], Equals(20130807))
        self.assertThat(json_dict['description'], Equals('20130806.1'))
        self.assertThat(json_dict['type'], Equals('full'))
        self.assertThat(json_dict['files'], HasLength(3))
