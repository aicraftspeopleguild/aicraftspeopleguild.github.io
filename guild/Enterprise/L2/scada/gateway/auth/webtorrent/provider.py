# -*- coding: utf-8 -*-
#
# ACG · auth.webtorrent tag provider (Jython 2.7)
#
# Flow: BitTorrent-style WebSocket tracker announces as peer discovery.
# Not really "auth" in the OAuth sense - sits under /auth because the
# info_hash (SHA-1 of the room name) is the bearer-token that proves
# membership in the mesh. Fallback chain + health probe are mirrored
# from /js/config.js TRACKERS[].
#
# Browser runtime: /js/p2p.js (connectTracker, announce).
#
from __future__ import print_function, division, absolute_import

try:
    import system
except ImportError:
    system = None

NAMESPACE = 'auth.webtorrent'
OWNED_PREFIXES = ('auth.webtorrent.',)

DEFAULT_TRACKERS = (
    'wss://tracker.openwebtorrent.com',
    'wss://tracker.webtorrent.dev',
    'wss://tracker.files.fm:7073/announce',
    'wss://tracker.novage.com.ua',
    'wss://tracker.sloppyta.co:443/announce',
    'wss://tracker.btorrent.xyz',
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

def seed_trackers(urls=None):
    chain = list(urls or DEFAULT_TRACKERS)
    for idx, url in enumerate(chain):
        write('trackers.%d' % idx, {
            '_udt': 'TrackerEndpoint',
            'url':   url,
            'state': 'unknown',
            'rttMs': None,
            'lastAt': None,
        })
    return chain


def set_tracker_state(idx, state, rtt_ms=None):
    if state not in ('unknown', 'ok', 'fail', 'trying', 'closed'):
        state = 'unknown'
    cur = read('trackers.%d' % idx) or {}
    cur.update({
        '_udt':  'TrackerEndpoint',
        'state': state,
        'rttMs': rtt_ms,
        'lastAt': system.date.now() if system else 0,
    })
    write('trackers.%d' % idx, cur)
    if state == 'ok':
        write('activeTracker', cur.get('url'))
        write('signedIn', True)
        if system is not None:
            write('signedInAt', system.date.now())
    return cur


def publish_announce(room, info_hash, tracker_url, num_want=50, n_offers=10):
    ann = {
        '_udt':    'AnnounceState',
        'room':    str(room),
        'infoHash':str(info_hash),
        'tracker': str(tracker_url),
        'numWant': int(num_want),
        'nOffers': int(n_offers),
        'ts':      system.date.now() if system else 0,
    }
    write('room', room)
    write('infoHash', info_hash)
    write('announce', ann)
    return ann


def bump_peers(seen=0, connected=0, offers=0, answers=0):
    cur = read('peers') or {'seen': 0, 'connected': 0, 'offers': 0, 'answers': 0}
    cur = {
        '_udt':      'PeerDiscovery',
        'seen':      int(cur.get('seen', 0)) + int(seen),
        'connected': int(cur.get('connected', 0)) + int(connected),
        'offers':    int(cur.get('offers', 0)) + int(offers),
        'answers':   int(cur.get('answers', 0)) + int(answers),
        'ts':        system.date.now() if system else 0,
    }
    write('peers', cur)
    return cur


def logout():
    for k in ('room', 'infoHash', 'activeTracker', 'announce',
              'peers', 'signedIn', 'signedInAt', 'lastError'):
        write(k, None)
