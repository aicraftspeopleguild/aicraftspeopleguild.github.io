# -*- coding: utf-8 -*-
#
# ACG · auth.webrtc tag provider (Jython 2.7)
#
# Flow: cryptographic peer-id identity.  No OAuth, no backend.  A fresh
# 20-byte BitTorrent-style peer id is generated in /js/config.js
# (-ACG001-<12 hex>) and that *is* the identity.  This provider mirrors
# that identity into the tag plant under auth.webrtc.* and keeps live
# connection stats.
#
# Browser runtime: /js/config.js (peer id) + /js/p2p.js (RTCPeerConnection).
#
from __future__ import print_function, division, absolute_import

try:
    import system
except ImportError:
    system = None

NAMESPACE = 'auth.webrtc'
OWNED_PREFIXES = ('auth.webrtc.',)

DEFAULT_STUN = (
    'stun:stun.l.google.com:19302',
    'stun:stun1.l.google.com:19302',
    'stun:stun2.l.google.com:19302',
)


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


def owns(path):
    for p in OWNED_PREFIXES:
        if path.startswith(p):
            return True
    return False


# ---- programs --------------------------------------------------------

def publish_identity(peer_id, emoji=None, fingerprint=None):
    """Called from /js/config.js (via sandbox bridge) after peer_id is minted."""
    short = peer_id[-8:] if peer_id else ''
    identity = {
        '_udt':      'WebRTCPeerIdentity',
        'provider':  'webrtc',
        'id':        peer_id,
        'shortId':   short,
        'emoji':     emoji or '',
        'fingerprint': fingerprint,
        'createdAt': system.date.now() if system else 0,
    }
    write('peerId', peer_id)
    write('shortId', short)
    write('identity', identity)
    write('signedIn', True)
    if system is not None:
        write('signedInAt', system.date.now())

    top_profile = {
        '_udt':     'Profile',
        'provider': 'webrtc',
        'id':       peer_id,
        'username': short,
        'avatar':   emoji or '',
    }
    if system is not None:
        system.tag.writeBlocking(['[ACG]auth/profile'], [top_profile])
        system.tag.writeBlocking(['[ACG]auth/signedIn'], [True])
    return identity


def publish_ice(stun_servers=None, turn_servers=None, policy=None):
    cfg = {
        '_udt':        'IceConfig',
        'stunServers': list(stun_servers or DEFAULT_STUN),
        'turnServers': list(turn_servers or []),
        'policy':      policy,
    }
    write('ice', cfg)
    return cfg


def publish_conn(state, peers, open_channels, bytes_sent=0, bytes_recv=0):
    stats = {
        '_udt':         'ConnStats',
        'state':        state,
        'peers':        int(peers),
        'openChannels': int(open_channels),
        'bytesSent':    int(bytes_sent),
        'bytesRecv':    int(bytes_recv),
        'ts':           system.date.now() if system else 0,
    }
    write('conn', stats)
    return stats


def logout():
    """Clear auth.webrtc.* and release top-level auth if we own it."""
    for k in ('peerId', 'shortId', 'identity', 'signedIn', 'signedInAt',
              'conn', 'lastError'):
        write(k, None)
    if system is not None:
        top = system.tag.readBlocking(['[ACG]auth/profile'])[0].value or {}
        if isinstance(top, dict) and top.get('provider') == 'webrtc':
            system.tag.writeBlocking(['[ACG]auth/profile'], [None])
            system.tag.writeBlocking(['[ACG]auth/signedIn'], [False])
