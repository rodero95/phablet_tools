# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# Copyright 2013 Canonical
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import subprocess
import logging


log = logging.getLogger()


def call(args):
    subprocess.check_call(args, shell=True)


def check_output(args):
    return subprocess.check_output(args, shell=True)


class AndroidBridge(object):
    '''Interface to adb.'''

    def __init__(self, device=None):
        if device:
            log.info('Setting adb for device %s' % device)
            self._adb_cmd = 'adb -s %s %%s' % device
        else:
            self._adb_cmd = 'adb %s'
        self._device = device

    @property
    def device(self):
        return self._device

    def push(self, src, dst):
        '''Performs and adb push.'''
        log.info('Pushing %s to %s' % (src, dst))
        cmd = 'push %s %s' % (src, dst)
        call(self._adb_cmd % cmd)

    def pull(self, src, dst):
        '''Performs and adb pull.'''
        log.info('Pulling %s to %s' % (src, dst))
        cmd = 'pull %s %s' % (src, dst)
        call(self._adb_cmd % cmd)

    def root(self):
        '''Set device to work as root.'''
        call(self._adb_cmd % 'root')
        call(self._adb_cmd % 'wait-for-device')

    def chmod(self, filename, mode):
        '''Performs a chmod on target device.'''
        cmd = 'shell chmod %s %s' % (mode, filename)
        call(self._adb_cmd % cmd)

    def getprop(self, android_property):
        '''Returns an android property.'''
        cmd = 'shell getprop %s ' % (android_property)
        return check_output(self._adb_cmd % cmd)

    def tcp_forward(self, src, dst):
        '''Creates a tcp forwarding rule.'''
        cmd = 'forward tcp:%s tcp:%s' % (src, dst)
        call(self._adb_cmd % cmd)

    def shell(self, command):
        '''Runs shell command and returns output'''
        cmd = 'shell %s' % command
        return check_output(self._adb_cmd % cmd)

    def chroot(self, command, root='data/ubuntu'):
        '''Runs command in chroot.'''
        log.debug('Running in chroot: %s' % command)
        cmd = 'shell "chroot %s %s"' % (root, command)
        call(self._adb_cmd % cmd)

    def reboot(self, recovery=False, bootloader=False):
        '''Reboots device.'''
        log.debug('Rebooting device')
        if recovery:
            cmd = 'reboot recovery'
        elif bootloader:
            cmd = 'reboot bootloader'
        else:
            cmd = 'reboot'
        call(self._adb_cmd % cmd)
