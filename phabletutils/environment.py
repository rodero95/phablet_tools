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

import hashlib
import logging
import os.path
import requests

from phabletutils.device import AndroidBridge
from phabletutils import cdimage
from phabletutils import community
from phabletutils import downloads
from phabletutils import hashes
from phabletutils import resources
from phabletutils import projects
from phabletutils import settings
from phabletutils import ubuntuimage

log = logging.getLogger()


def get_ubuntu_stamp(uri):
    '''Downloads the jenkins build id from stamp file'''
    try:
        ubuntu_stamp = requests.get('%s/quantal-ubuntu_stamp' % uri)
        if ubuntu_stamp.status_code != 200:
            ubuntu_stamp = requests.get('%s/ubuntu_stamp' % uri)
        if ubuntu_stamp.status_code != 200:
            log.error('Latest build detection not supported... bailing')
            exit(1)
        # Make list and get rid of empties
        build_data = filter(lambda x: x.startswith('JENKINS_BUILD='),
                            ubuntu_stamp.content.split('\n'))
        jenkins_build_id = build_data[0].split('=')[1]
    except (requests.HTTPError, requests.Timeout, requests.ConnectionError):
        log.error('Could not download build data from jenkins... bailing')
        exit(1)
    except IndexError:
        raise EnvironmentError('Jenkins data format has changed, incompatible')
    return jenkins_build_id


def detect_device(serial, device=None):
    '''If no argument passed determine them from the connected device.'''
    # Check CyanogenMod property
    if not device:
        adb = AndroidBridge(serial)
        adb.start()
        device = adb.getprop('ro.cm.device').strip()
    # Check Android property
    if not device:
        device = adb.getprop('ro.product.device').strip()
    log.info('Device detected as %s' % device)
    # property may not exist or we may not map it yet
    if device not in settings.supported_devices:
        raise EnvironmentError('Unsupported device, autodetect fails device')
    return device


#def setup_revision1(device, uri, download_dir, settings):
#    if not uri:
#        uri = settings.download_uri
#    if not download_dir:
#        build = get_ubuntu_stamp(uri)
#        download_dir = get_full_path(
#            os.path.join(settings.download_dir, build))
#        setup_download_directory(download_dir)
#    else:
#        uri = None
#    system = settings.device_file_img % device
#    boot = settings.boot_file_img % (device,)
#    hash_dict = {entry: load_hash(uri, '%s.md5sum' % entry, download_dir)
#              for entry in (system, boot)}
#    if uri:
#        system_uri = '%s/%s' % (uri, system),
#        boot_uri = '%s/%s' % (uri, boot),
#    else:
#        system_uri = None
#        boot_uri = None
#    system_file = resources.File(file_path=os.path.join(download_dir, system),
#                                 file_uri=system_uri,
#                                 file_hash=hashes[system],
#                                 file_hash_func=hashlib.md5)
#    boot_file = resources.File(file_path=os.path.join(download_dir, boot),
#                               file_uri=boot_uri,
#                               file_hash=hashes[boot],
#                               file_hash_func=hashlib.md5)
#    return projects.Android(boot=boot_file, system=system_file)


def setup_cdimage_files(project_name, uri, download_dir, series,
                        device, legacy=False):
    downloads.setup_download_directory(download_dir)
    templ_arch_any = settings.files_arch_any[project_name]
    templ_arch_all = settings.files_arch_all[project_name]
    file_names = {}
    for key in templ_arch_any:
        file_names[key] = templ_arch_any[key] % (series, device)
    for key in templ_arch_all:
        file_names[key] = templ_arch_all[key] % series
    if legacy:
        hash_func = hashlib.md5
        hash_dict = {}
        for key in file_names:
            file_hash = hashes.load_hash(uri, '%s.md5sum' %
                                         file_names[key], download_dir)
            hash_dict[file_names[key]] = file_hash[file_names[key]]
    else:
        hash_func = hashlib.sha256
        hash_dict = hashes.load_hash(uri, 'SHA256SUMS', download_dir)
    files = {}
    for key in file_names:
        if uri:
            file_uri = '%s/%s' % (uri, file_names[key])
        else:
            file_uri = None
        files[key] = resources.File(
            file_path=os.path.join(download_dir, file_names[key]),
            file_uri=file_uri,
            file_hash=hash_dict[file_names[key]],
            file_hash_func=hash_func)
    return files


def setup_cdimage_touch(args):
    device = detect_device(args.serial, args.device)
    series = args.series
    base_uri = '%s/%s' % (settings.cdimage_uri_base, args.project)

    if args.base_path:
        uri = None
        download_dir = args.base_path
    else:
        daily_uri = '%s/daily-preinstalled' % (base_uri, )
        build = cdimage.get_build(daily_uri, args.pending)
        uri = '%s/%s' % (daily_uri, build)
        download_dir = downloads.get_full_path(
            os.path.join(settings.download_dir, args.project, build))
    files = setup_cdimage_files(
        args.project, uri, download_dir, series, device)
    return cdimage_project(files, args)


def setup_cdimage_legacy(args):
    series = args.series
    uri = args.uri
    device = detect_device(args.serial, args.device)
    if args.base_path:
        download_dir = args.base_path
    elif args.revision or args.latest_revision:
        build = args.build
        uri = args.uri
        download_dir = downloads.get_full_path(
            os.path.join(args.project, series, build))
    else:
        base_uri = '%s/%s' % (settings.cdimage_uri_base, args.project)
        daily_uri = '%s/daily-preinstalled' % (base_uri, )
        build = cdimage.get_build(daily_uri)
        uri = '%s/%s' % (daily_uri, build)
        download_dir = downloads.get_full_path(
            os.path.join(settings.download_dir, args.project, build))
    files = setup_cdimage_files(
        args.project, uri, download_dir, series, device, legacy=True)
    return cdimage_project(files, args)


def cdimage_project(files, args):
    if args.bootstrap:
        return projects.UbuntuTouchBootstrap(
            system=files['system_img'],
            boot=files['boot_img'],
            recovery=files['recovery_img'],
            ubuntu=files['ubuntu_zip'])
    else:
        if args.device_path:
            files['device_zip'] = args.device_path
        if args.ubuntu_path:
            files['ubuntu_zip'] = args.ubuntu_path
        return projects.UbuntuTouchRecovery(
            device=files['device_zip'],
            ubuntu=files['ubuntu_zip'],
            wipe=args.wipe)


def setup_ubuntu_system(args):
    device = detect_device(args.serial, args.device)
    if args.revision <= 0:
        json = ubuntuimage.get_json_from_index(device, args.revision)
    else:
        raise EnvironmentError('Specific version retrieve not supported yet')
    download_dir = downloads.get_full_path(os.path.join(
        settings.download_dir, args.project, str(json['version'])))
    uri = settings.system_image_uri
    files, command_part = ubuntuimage.get_files(download_dir, uri, json)
    recovery = cdimage.get_file(file_key='recovery_img',
                                series=args.series,
                                download_dir=download_dir,
                                device=device)
    return projects.UbuntuTouchSystem(
        file_list=files,
        command_part=command_part,
        recovery=recovery)


def setup_community(args):
    config_dir = community.branch_project(args.device)
    json_dict = community.load_manifest(config_dir)
    download_dir = community.get_download_dir(
        args.device, json_dict['revision'])
    files = community.get_files(json_dict, download_dir, args.series)
    return projects.UbuntuTouchRecovery(
        device=files['device'],
        ubuntu=files['ubuntu'],
        storage=json_dict['storage'],
        wipe=args.wipe)


def list_revisions(args):
    # Easy hack to get rid of the logger and inhibit requests from logging
    log.setLevel(logging.FATAL)
    revisions = cdimage.get_available_revisions(args.uri)
    cdimage.display_revisions(revisions)
