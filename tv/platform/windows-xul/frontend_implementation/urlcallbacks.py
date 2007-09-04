# Miro - an RSS based video player application
# Copyright (C) 2005-2007 Participatory Culture Foundation
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

"""Handles installing callbacks for url loads of HTMLDisplay objects.

The way this module is used is HTMLDisplay installs a bunch of callbacks with
installCallback(), then the mycontentpolicy XPCOM object calls runCallback()
when it sees a new URL.  This means that installCallback is called from the
backend event loop, while runCallback is called from the frontend event loop.
"""

import config
import util
import prefs
from threading import Lock

callbacks = {}
mainDisplayCallback = None
# We assume all urls that don't begin with file:// go to the mainDisplay
# FIXME: we may want a cleaner way to do this.
callbacksLock = Lock()

def installCallback(referrer, callback):
    """Install a new URL load callback, callback will be called when we see a
    URL load where the referrer matches referrer.
    Callback should accept a URL as an input and return True if we should
    continue the load, or False if the we shouldn't.
    """
    callbacksLock.acquire()
    try:
        callbacks[referrer] = callback
    finally:
        callbacksLock.release()

def installMainDisplayCallback(callback):
    """Install a callback for urls where the referrerer is any channel guide
    page.  """
    global mainDisplayCallback
    callbacksLock.acquire()
    try:
        mainDisplayCallback = callback
    finally:
        callbacksLock.release()

def removeCallback(referrer):
    """Remove a callback created with installCallback().  If a callback
    doesn't exist for referrer, a KeyError will be thrown.
    """
    callbacksLock.acquire()
    try:
        del callbacks[referrer]
    finally:
        callbacksLock.release()

def runCallback(referrerURL, url):
    """Try to find an installed callback and run it if there is one.  If this
    method return True, the URL load should continue, if it returns False it
    should stop.
    """

    callbacksLock.acquire()
    try:
        try:
            callback = callbacks[referrerURL]
        except KeyError:
            if (not url.startswith("file://") and 
                    mainDisplayCallback is not None):
                callback = mainDisplayCallback
            else:
                return True
    finally:
        callbacksLock.release()
    try:
        rv = callback(url)
        return rv
    except:
        util.failedExn(when="When running URL callback")
        return True
