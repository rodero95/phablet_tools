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

import os
import logging

log = logging.getLogger()


def accepted(pathname):
    '''
    Remember that the user accepted the license.
    '''
    open(pathname, 'w').close()


def has_accepted(pathname):
    '''
    Return True if the user accepted the license once.
    '''
    return os.path.exists(pathname)


def query(message, accept_path):
    '''Display end user agreement to continue with deployment.'''
    try:
        while True:
            print message
            print 'Do you accept? [yes|no]'
            answer = raw_input().lower()
            if answer == 'yes':
                accepted(accept_path)
                return True
            elif answer == 'no':
                return False
    except KeyboardInterrupt:
        log.error('Interruption detected, cancelling install')
        return False
