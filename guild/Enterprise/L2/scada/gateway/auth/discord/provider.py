# -*- coding: utf-8 -*-
#
# ACG · auth.discord tag provider (Jython 2.7)
#
# Flow: OAuth 2.0 implicit grant (response_type=token).  Pure browser —
# no backend or CORS proxy required.  Browser runtime lives in
# /js/auth.js (discordLogin / discordFinish).
#
from __future__ import print_function, division, absolute_import

try:
    import system
except ImportError:
    system = None

NAMESPACE = 'auth.discord'
AUTHORIZE_URL = 'https://discord.com/oauth2/authorize'
USERINFO_URL  = 'https://discord.com/api/users/@me'
OWNED_PREFIXES = ('auth.discord.',)


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

def publish_profile(discord_user):
    """discord_user = dict from Discord /users/@me response."""
    udt = {
        '_udt':          'DiscordProfile',
        'provider':      'discord',
        'id':            discord_user.get('id'),
        'username':      discord_user.get('username'),
        'global_name':   discord_user.get('global_name'),
        'avatar':        discord_user.get('avatar'),
        'discriminator': discord_user.get('discriminator'),
        'verified':      discord_user.get('verified'),
    }
    write('profile', udt)
    write('signedIn', True)
    if system is not None:
        write('signedInAt', system.date.now())
    # promote to the top-level auth.profile (canonical identity)
    try:
        import auth.provider as top
        top.publish_profile({
            'provider': 'discord',
            'id':       udt['id'],
            'username': udt['global_name'] or udt['username'],
            'avatar':   _avatar_url(udt['id'], udt['avatar']),
        })
    except Exception:
        pass


def _avatar_url(user_id, avatar):
    if avatar:
        return 'https://cdn.discordapp.com/avatars/%s/%s.png?size=64' % (user_id, avatar)
    idx = int(user_id) >> 22 if user_id else 0
    return 'https://cdn.discordapp.com/embed/avatars/%d.png' % (idx % 6)


def set_token_expiry(expires_in_sec):
    if system is None:
        return
    write('tokenExpiresAt', system.date.addSeconds(system.date.now(), int(expires_in_sec)))


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
