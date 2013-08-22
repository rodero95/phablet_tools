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

"""Holds different projects or ways Ubuntu Touch is delivered."""

import os
import os.path
import tempfile
import logging
import gzip

from phabletutils.downloads import checksum_verify
from phabletutils.resources import (File, SignedFile)
from phabletutils import downloads
from time import sleep
from textwrap import dedent

log = logging.getLogger()


def gunzip(file_path):
    if not file_path.endswith('.gz'):
        return file_path
    target_path = file_path[:-3]
    log.info('Decompressing %s' % file_path)
    with open(target_path, 'wb') as target_file:
        with gzip.open(file_path, 'r') as gzip_file:
            for chunk in gzip_file.read():
                target_file.write(chunk)
    return target_path


def wipe_device(adb):
    log.info('Clearing /data and /cache')
    adb.shell('mount /data')
    adb.shell('rm -Rf /cache/* /data/* /data/.developer_mode')
    adb.shell('mkdir /cache/recovery')
    adb.shell('mkdir /data/media')


class BaseProject(object):
    """A provisioning mechanism for all the projects."""

    def __init__(self, recovery=None, system=None, boot=None,
                 device=None, ubuntu=None, wipe=False):
        self._list = []
        for item in (recovery, system, boot, device, ubuntu):
            if item and not isinstance(item, File):
                raise TypeError('%s is not of type File' % item)
            elif item:
                self._list.append(item)
                if item.check and not item.uri and not item.verified:
                    raise EnvironmentError(
                        '%s is not on disk' % item.path)

        self._recovery = recovery
        self._system = system
        self._boot = boot
        self._device = device
        self._ubuntu = ubuntu
        self._wipe = wipe

    def download(self):
        """Downloads and verifies resources."""
        download_list = filter((lambda x: x.check), self._list)
        download_list = filter((lambda x: not x.verified), download_list)
        log.debug('Download list %s' % download_list)
        if not download_list:
            log.info('Download not required')
            return
        for entry in download_list:
            log.debug('Download entry %s %s' % (entry.path, entry.verified))
            downloads.download(entry)
            if entry.hash and \
               not checksum_verify(entry.path, entry.hash, entry.hash_type):
                raise EnvironmentError(
                    'Checksum does not match after download for %s '
                    'and hash %s' % (entry.path, entry.hash))
        download_list = filter(lambda x: isinstance(x, SignedFile), self._list)
        for entry in download_list:
            downloads.download_sig(entry)

    def install(self):
        raise EnvironmentError('Requires implementation')


class Android(BaseProject):
    """Standard Android Project."""

    def __init__(self, boot, system):
        super(Android, self).__init__(boot=boot, system=system)

    def install(self, adb, fastboot):
        log.warning('Device needs to be unlocked for the following to work')
        fastboot.flash('system', gunzip(self.system))
        fastboot.flash('boot', self.boot)
        log.info('Installation will complete soon and reboot into Android')
        fastboot.reboot()


class UbuntuTouchBootstrap(BaseProject):

    def __init__(self, boot, system, recovery, ubuntu):
        log.debug('UbuntuTouchBootstrap '
                  'boot: %s, system: %s, recovery: %s, ubuntu: %s' %
                  (boot.path, system.path, recovery.path, ubuntu.path))
        super(UbuntuTouchBootstrap, self).__init__(
            boot=boot, system=system, recovery=recovery, ubuntu=ubuntu,
            wipe=True)

    def install(self, adb, fastboot):
        adb.reboot(bootloader=True)
        log.warning('Device needs to be unlocked for the following to work')
        fastboot.flash('system', self._system.path)
        fastboot.flash('boot', self._boot.path)
        fastboot.flash('recovery', self._recovery.path)
        fastboot.boot(self._recovery.path)
        sleep(15)
        wipe_device(adb)
        adb.push(self._ubuntu.path, '/sdcard/autodeploy.zip')
        log.info('Deploying Ubuntu')
        adb.reboot(recovery=True)
        log.info('Installation will complete soon and reboot into Ubuntu')


class UbuntuTouchRecovery(BaseProject):

    recovery_script_template = dedent('''\
                                      mount("{0}");
                                      install_zip("{1}");
                                      install_zip("{2}");
                                      ''')

    def __init__(self, device, ubuntu, storage='/sdcard/', wipe=False):
        log.debug('UbuntuTouchRecovery device: %s, ubuntu: %s, wipe: %s' %
                  (device.path, ubuntu.path, wipe))
        super(UbuntuTouchRecovery, self).__init__(
            ubuntu=ubuntu, device=device, wipe=wipe)
        self._storage = storage

    def install(self, adb, fastboot=None):
        """
        Deploys recovery files, recovery script and then reboots to install.
        """
        log.warning('The device needs to have a clockwork mod recovery image '
                    '(or one that supports extendedcommands) '
                    'in place for the provisioning to work')
        adb.reboot(recovery=True)
        sleep(20)
        if self._wipe:
            wipe_device(adb)
        adb.shell('mount %s' % self._storage)
        adb.push(self._device.path, self._storage)
        adb.push(self._ubuntu.path, self._storage)
        recovery_file = self.create_recovery_file()
        adb.push(recovery_file, '/cache/recovery/extendedcommand')
        adb.reboot(recovery=True)
        log.info('Once completed the device should reboot into Ubuntu')
        log.debug('Removing recovery file %s' % recovery_file)
        os.unlink(recovery_file)

    def create_recovery_file(self):
        template = self.recovery_script_template
        recovery_file = tempfile.NamedTemporaryFile(delete=False)
        device = os.path.join(self._storage,
                              os.path.basename(self._device.path))
        ubuntu = os.path.join(self._storage,
                              os.path.basename(self._ubuntu.path))
        recovery_script = template.format(self._storage, device, ubuntu)
        with recovery_file as output_file:
            output_file.write(recovery_script)
        return recovery_file.name


class UbuntuTouchSystem(BaseProject):

    ubuntu_recovery_script = dedent('''\
        format data
        format system
        load_keyring image-master.tar.xz image-master.tar.xz.asc
        load_keyring image-signing.tar.xz image-signing.tar.xz.asc
        mount system
        ''')

    def __init__(self, file_list, recovery, command_part):
        log.debug('UbuntuTouchSystem')
        super(UbuntuTouchSystem, self).__init__(recovery=recovery, wipe=True)
        for item in file_list:
            if item and not isinstance(item, File):
                raise TypeError('%s is not of type File' % item)
            elif item:
                self._list.append(item)
        self._recovery_list = file_list
        self._command_part = command_part

    def install(self, adb, fastboot=None):
        """
        Deploys recovery files, recovery script and then reboots to install.
        """
        adb.reboot(recovery=True)
        sleep(20)
        wipe_device(adb)

        for entry in self._recovery_list:
            adb.push(entry.path, '/cache/recovery/')
            try:
                adb.push(entry.sig_path, '/cache/recovery/')
            except AttributeError:
                pass
        adb.push(self.create_ubuntu_command_file(),
                 '/cache/recovery/ubuntu_command')
        adb.reboot(bootloader=True)
        fastboot.flash('recovery', self._recovery.path)
        fastboot.boot(self._recovery.path)
        log.info('Once completed the device should reboot into Ubuntu')

    def create_ubuntu_command_file(self):
        ubuntu_command_file = tempfile.NamedTemporaryFile(delete=False)
        with ubuntu_command_file as output_file:
            output_file.write(self.ubuntu_recovery_script)
            output_file.write(self._command_part)
            output_file.write('unmount system\n')
        return ubuntu_command_file.name
