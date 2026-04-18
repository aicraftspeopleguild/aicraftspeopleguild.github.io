# -*- coding: utf-8 -*-
#
# ACG · auth.github tag provider (Jython 2.7)
#
# Flow: OAuth 2.0 device authorisation grant.  github.com's OAuth
# endpoints don't send CORS headers, so a small CORS proxy is required.
# The proxy holds no secret — it only relays two POSTs.  Browser runtime
# lives in /js/auth.js (githubLogin / githubFinish).
#
from __future__ import print_function, division, absolute_import

try:
    import system
except ImportError:
    system = None

NAMESPACE = 'auth.github'
DEVICE_URL  = '/login/device/code'          # appended to configured proxyUrl
TOKEN_URL   = '/access_token'
USERINFO_URL = 'https://api.github.com/user'
OWNED_PREFIXES = ('auth.github.',)


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


def inc(key, by=1):
    cur = read(key) or 0
    write(key, cur + by)
    return cur + by


# ---- programs --------------------------------------------------------

def start_device_flow(device_code):
    """device_code = dict returned from POST /device/code via proxy."""
    write('deviceCodeInFlight', True)
    write('verificationUri', device_code.get('verification_uri'))
    write('userCode',        device_code.get('user_code'))
    write('pollCount',       0)


def poll_once():
    inc('pollCount')


def end_device_flow(success, msg=None):
    write('deviceCodeInFlight', False)
    write('verificationUri', None)
    write('userCode', None)
    if not success and msg:
        write('lastError', str(msg))


def publish_profile(github_user):
    """github_user = dict from GET api.github.com/user response."""
    udt = {
        '_udt':      'GithubProfile',
        'provider':  'github',
        'id':        str(github_user.get('id')),
        'login':     github_user.get('login'),
        'name':      github_user.get('name'),
        'avatar_url':github_user.get('avatar_url'),
        'html_url':  github_user.get('html_url'),
        'bio':       github_user.get('bio'),
    }
    write('profile', udt)
    write('signedIn', True)
    if system is not None:
        write('signedInAt', system.date.now())
    try:
        import auth.provider as top
        top.publish_profile({
            'provider': 'github',
            'id':       udt['id'],
            'username': udt['login'],
            'avatar':   udt['avatar_url'],
        })
    except Exception:
        pass


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
