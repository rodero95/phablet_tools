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

revision = 2
default_series = 'saucy'
cdimage_uri_base = 'http://cdimage.ubuntu.com'
system_image_uri = 'https://system-image.ubuntu.com'
download_dir = 'phablet-flash'

files_arch_any = {
    'ubuntu-touch': {
        'device_zip': '%s-preinstalled-touch-armel+%s.zip',
        'system_img': '%s-preinstalled-system-armel+%s.img',
        'boot_img': '%s-preinstalled-boot-armhf+%s.img',
        'recovery_img': '%s-preinstalled-recovery-armel+%s.img',
    },
    'ubuntu-touch-preview': {
        'device_zip': '%s-preinstalled-armel+%s.zip',
        'system_img': '%s-preinstalled-system-armel+%s.img',
        'boot_img': '%s-preinstalled-boot-armel+%s.img',
        'recovery_img': '%s-preinstalled-recovery-armel+%s.img',
    },
}

files_arch_all = {
    'ubuntu-touch': {
        'ubuntu_zip': '%s-preinstalled-touch-armhf.zip',
    },
    'ubuntu-touch-preview': {
        'ubuntu_zip': '%s-preinstalled-phablet-armhf.zip',
    }
}

recovery_script_template = '''boot-recovery
--update_package=/sdcard/{0}
--user_data_update_package=/sdcard/{1}
reboot
'''

supported_devices = ('mako',
                     'maguro',
                     'manta',
                     'grouper',
                     )
legal_notice = '''"Touch Developer Preview for Ubuntu" is released for free
non-commercial use. It is provided without warranty, even the implied
warranty of merchantability, satisfaction or fitness for a particular
use. See the licence included with each program for details.

Some licences may grant additional rights; this notice shall not limit
your rights under each program's licence. Licences for each program
are available in the usr/share/doc directory. Source code for Ubuntu
can be downloaded from archive.ubuntu.com. Ubuntu, the Ubuntu logo
and Canonical are registered trademarks of Canonical Ltd. All other
trademarks are the property of their respective owners.

"Touch Preview for Ubuntu" is released for limited use due to the
inclusion of binary hardware support files. The original components
and licenses can be found at:
https://developers.google.com/android/nexus/drivers.
'''
accept_path = '~/.phablet_accepted'
