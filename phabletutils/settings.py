#! /usr/bin/env python
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

download_uri = 'http://cdimage.ubuntu.com/ubuntu-touch-preview/quantal/mwc-demo'
daily_uri = 'http://cdimage.ubuntu.com/ubuntu-touch-preview/daily-preinstalled/current'
download_dir = 'phablet-flash'
ubuntu_image = 'quantal-preinstalled-phablet-armhf.zip'
device_file = 'quantal-preinstalled-armel+%s.zip'
device_file_img = 'quantal-preinstalled-system-armel+%s.img'
boot_file_img = 'quantal-preinstalled-boot-armel+%s.img'
recovery_file_img = 'quantal-preinstalled-recovery-armel+%s.img'
recovery_script_template = '''boot-recovery
--update_package={0}/{1}
--user_data_update_package={0}/{2}
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
