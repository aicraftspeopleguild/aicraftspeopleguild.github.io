# -*- coding: utf-8 -*-
#
# ACG · auth tag provider (Jython 2.7)
#
# Owns: auth.*
# Browser runtime: /js/auth.js
#
from __future__ import print_function, division, absolute_import

try:
    import system
except ImportError:
    system = None

NAMESPACE = 'auth'
OWNED_PREFIXES = ('auth.',)


def _tag_path(key):
    return '[ACG]%s/%s' % (NAMESPACE, key)


def write(key, value):
    if system is None:
        return
    system.tag.writeBlocking([_tag_path(key)], [value])


def read(key):
    if system is None:
        return None
    return system.tag.readBlocking([_tag_path(key)])[0].value


# ---- programs --------------------------------------------------------

def publish_profile(profile):
    """profile := dict or None."""
    if profile is None:
        write('profile', None)
        write('signedIn', False)
        return
    # coerce fields into the Profile UDT shape
    udt = {
        '_udt':     'Profile',
        'provider': profile.get('provider'),
        'id':       profile.get('id'),
        'username': profile.get('username'),
        'avatar':   profile.get('avatar'),
    }
    write('profile', udt)
    write('signedIn', True)


def logout():
    publish_profile(None)


def owns(path):
    for p in OWNED_PREFIXES:
        if path.startswith(p):
            return True
    return False
