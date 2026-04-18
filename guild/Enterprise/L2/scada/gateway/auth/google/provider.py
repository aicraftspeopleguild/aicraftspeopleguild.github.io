# -*- coding: utf-8 -*-
#
# ACG · auth.google tag provider (Jython 2.7)
#
# Flow: OIDC implicit (response_type=id_token).  Pure browser, no proxy —
# the id_token is a signed JWT we verify locally against Google's JWKS.
#
# STATUS: scaffold.  The browser runtime at /js/auth.js does not yet
# implement googleLogin; this module mirrors the discord/github shape so
# the wiring is ready when the front-end catches up.
#
from __future__ import print_function, division, absolute_import

try:
    import system
except ImportError:
    system = None

NAMESPACE = 'auth.google'
AUTHORIZE_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
JWKS_URL      = 'https://www.googleapis.com/oauth2/v3/certs'
OWNED_PREFIXES = ('auth.google.',)


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

def publish_profile(claims):
    """claims = decoded id_token payload."""
    udt = {
        '_udt':           'GoogleProfile',
        'provider':       'google',
        'id':             claims.get('sub'),
        'email':          claims.get('email'),
        'email_verified': claims.get('email_verified'),
        'name':           claims.get('name'),
        'given_name':     claims.get('given_name'),
        'family_name':    claims.get('family_name'),
        'picture':        claims.get('picture'),
        'locale':         claims.get('locale'),
    }
    write('profile', udt)
    write('signedIn', True)
    if system is not None:
        write('signedInAt', system.date.now())
    try:
        import auth.provider as top
        top.publish_profile({
            'provider': 'google',
            'id':       udt['id'],
            'username': udt['name'] or udt['email'],
            'avatar':   udt['picture'],
        })
    except Exception:
        pass


def set_token_expiry(exp_sec):
    if system is None:
        return
    # exp claim is seconds since epoch
    write('tokenExpiresAt', int(exp_sec) * 1000)


def note_error(msg):
    write('lastError', str(msg))


def logout():
    write('signedIn', False)
    write('profile', None)
    try:
        import auth.provider as top
        top.logout()
    except Exception:
        pass


def owns(path):
    for p in OWNED_PREFIXES:
        if path.startswith(p):
            return True
    return False
