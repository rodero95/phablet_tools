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

import argparse
import logging
import tempfile
import urllib
import urlparse

from phabletutils import cdimage
from phabletutils import environment
from phabletutils import resources
from phabletutils import settings

log = logging.getLogger()


class PathAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        log.debug('PathAction: %r %r %r' %
                  (namespace, values, option_string))
        uri = urlparse.urlparse(values)
        if not uri.scheme or uri.scheme == 'file':
            if '%' in uri.path:
                zip_file_path = urllib.unquote(
                    urlparse.urlparse(uri.path))
            else:
                zip_file_path = uri.path
            zip_file_uri = None
            check = False
        elif uri.scheme == 'http' or uri.scheme == 'https':
            zip_file_path = tempfile.mktemp()
            zip_file_uri = values
            check = True
        log.debug('Download from %s, path on disk %s' %
                  (zip_file_uri, zip_file_path))
        artifact = resources.File(file_path=zip_file_path,
                                  file_uri=zip_file_uri,
                                  check=check)
        setattr(namespace, self.dest, artifact)


class RevisionListAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        log.debug('RevisionListAction: %r %r %r' %
                  (namespace, values, option_string))
        project = 'ubuntu-touch-preview'
        uri = '%s/%s' % (settings.cdimage_uri_base, project)
        setattr(namespace, 'func', environment.list_revisions)
        setattr(namespace, 'uri', uri)


class RevisionAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        log.debug('RevisionAction: %r %r %r' %
                  (namespace, values, option_string))
        project = 'ubuntu-touch-preview'
        base_uri = '%s/%s' % (settings.cdimage_uri_base, project)
        if values:
            revision_split = values.split('/')
            if len(revision_split) != 2:
                raise EnvironmentError(
                    'Improper use of revision, needs to be formatted like'
                    '[series]/[revision]. Use --list-revisions to find'
                    'the available revisions on cdimage')
            series = revision_split[0]
            build = revision_split[1]
        else:
            series, build = cdimage.get_latest_revision(base_uri)
        uri = '%s/%s/%s' % (base_uri, series, build)
        setattr(namespace, self.dest, True)
        setattr(namespace, 'series', series)
        setattr(namespace, 'build', build)
        setattr(namespace, 'uri', uri)


def cdimage_touch(parent_parser, parents):
    parser = parent_parser.add_parser(
        'cdimage-touch', parents=parents,
        help='Provisions the device with a CDimage build of Ubuntu Touch.')
    parser.set_defaults(func=environment.setup_cdimage_touch,
                        project='ubuntu-touch',
                        series=settings.default_series,
                        build=None,
                        uri=None)
    parser.add_argument('-b',
                        '--bootstrap',
                        help='''Bootstrap the target device, this only
                                works on Nexus devices or devices that
                                use fastboot and are unlocked. All user
                                data is destroyed''',
                        action='store_true')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--pending',
                       action='store_true',
                       required=False,
                       help='Get pending link from cdimage')
    group.add_argument('-p',
                       '--base-path',
                       required=False,
                       default=None,
                       help='''Installs from base path, you must have
                               the same directory structure as if you
                               downloaded for real.
                               This option is completely offline.''')
    return parser


def ubuntu_system(parent_parser, parents):
    parser = parent_parser.add_parser(
        'ubuntu-system', parents=parents,
        help='Provisions the device with an Ubuntu Image Based Upgrade image.')
    parser.set_defaults(func=environment.setup_ubuntu_system,
                        revision=0,
                        series=settings.default_series,
                        project='imageupdates')
    parser.add_argument('--revision',
                        type=int,
                        help='''Download a relative revision from current
                                (-1, -2, ...) or a specific version.''')
    return parser


def legacy(parent_parser, parents):
    parser = parent_parser.add_parser(
        'cdimage-legacy', parents=parents,
        help='Provisions the device with legacy unflipped images.')
    parser.set_defaults(func=environment.setup_cdimage_legacy,
                        project='ubuntu-touch-preview',
                        series=settings.default_series,
                        build=None,
                        uri=None)
    parser.add_argument('-b',
                        '--bootstrap',
                        help='''Bootstrap the target device, this only
                                works on Nexus devices or devices that
                                use fastboot and are unlocked. All user
                                data is destroyed''',
                        action='store_true')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--list-revisions',
                       action=RevisionListAction,
                       nargs=0,
                       help='List available revisions on cdimage and exits')
    group.add_argument('-r',
                       '--revision',
                       action=RevisionAction,
                       help='''Choose a specific release to install
                               from cdimage, the format is
                               [series]/[rev].''')
    group.add_argument('-l',
                       '--latest-revision',
                       action=RevisionAction,
                       nargs=0,
                       help='''Pulls the latest tagged revision.''')
    group.add_argument('-p',
                       '--base-path',
                       required=False,
                       default=None,
                       help='''Installs from base path, you must have
                               the same directory structure as if you
                               downloaded for real.
                               This option is completely offline.''')
    return parser


def community(parent_parser, parents):
    parser = parent_parser.add_parser(
        'community', parents=parents,
        help='Provisions the device with a community supported build.')
    parser.add_argument('-d', '--device', required=True,
                        help='''Specify device to flash.
                                Find out more about flashable devices at
                                https://wiki.ubuntu.com/Touch/Devices''')
    parser.set_defaults(func=environment.setup_community,
                        series=settings.default_series)
    return parser


def common_non_system():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--device-path',
                        action=PathAction,
                        help='''uri to device zip to flash,
                                e.g.; file:///..., http://.''',)
    parser.add_argument('--ubuntu-path',
                        action=PathAction,
                        help='''uri to ubuntu zip to flash,
                                e.g.; file:///..., http://.''',)
    parser.add_argument('--wipe',
                        action='store_true',
                        help='''Wipes device data.''')
    return parser


def common_supported():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-d',
                        '--device',
                        help='''Target device to deploy.''',
                        required=False,
                        choices=settings.supported_devices)
    return parser


def common():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--debug',
                        action='store_true',
                        help='''Enable debug messages.''')
    parser.add_argument('-s',
                        '--serial',
                        help='''Device serial. Use when more than
                                one device is connected.''')
    parser.add_argument('-D',
                        '--download-only',
                        action='store_true',
                        help='Download image only, but do not flash device.')
    return parser


def get_parser():
    """
    Returns a Namespace of the parsed arguments from the command line.
    """
    parser = argparse.ArgumentParser(

        description='''phablet-flash is used to provision devices.
                       It does a best effort to deploy in different ways.''',
        epilog='''Use -h or --help after each command to learn about
                  their provisioning options.''')
    # Parsers
    common_parser = common()
    common_supported_parser = common_supported()
    common_non_system_parser = common_non_system()
    sub = parser.add_subparsers(title='Commands', metavar='')
    cdimage_touch(sub, [common_parser, common_supported_parser,
                        common_non_system_parser])
    legacy(sub, [common_parser, common_supported_parser,
                 common_non_system_parser])
    ubuntu_system(sub, [common_parser, common_supported_parser, ])
    community(sub, [common_parser, common_non_system_parser, ])
    return parser
