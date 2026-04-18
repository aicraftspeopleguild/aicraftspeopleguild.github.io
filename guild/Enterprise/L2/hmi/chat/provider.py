# -*- coding: utf-8 -*-
#
# ACG · chat tag provider (Jython 2.7 · Ignition gateway script)
#
# Owns: chat.*, room.*, tracker.*, peers.*, signal.*
#
# This file is the canonical server-side provider.  The browser runtime
# (/js/p2p.js, /js/peers.js, /js/chat.js) writes the same tag paths from
# the client.  Inside Ignition this module is imported from a gateway
# event script and dispatched by /ignition-host/ (if deployed).
#
# Jython 2.7 — deliberately NOT Python 3.  The `print_function` import
# keeps the syntax valid on both but forbids Py3-only features.
#
from __future__ import print_function, division, absolute_import

try:
    import system                                  # Ignition built-in
except ImportError:                                # running outside gateway
    system = None

NAMESPACE = 'chat'
OWNED_PREFIXES = ('chat.', 'room.', 'tracker.', 'peers.', 'signal.')


# ---- tag plumbing ----------------------------------------------------

def _tag_path(key):
    # Ignition tag syntax: [TagProvider]Folder/Name
    return '[ACG]%s/%s' % (NAMESPACE, key)


def write(key, value, quality='good'):
    if system is None:
        return
    system.tag.writeBlocking([_tag_path(key)], [value])


def read(key):
    if system is None:
        return None
    qv = system.tag.readBlocking([_tag_path(key)])[0]
    return qv.value


def inc(key, by=1):
    cur = read(key) or 0
    write(key, cur + by)
    return cur + by


# ---- programs --------------------------------------------------------
# Each function mirrors a program in /scada/programs/acg/*.json.
# See /chat/udts.json for the shapes.

def add_msg(peer_id, name, emoji, text, is_system=False):
    """Called when a new chat message arrives from a peer."""
    if is_system:
        return
    my_id = read('myId')
    if peer_id == my_id:
        inc('msgsOut')
    else:
        inc('msgsIn')
    if system is not None:
        write('lastMsgAt', system.date.now())


def send(text):
    """User sends a chat message.  Browser handles bcast; we bump tags."""
    inc('msgsOut')
    if system is not None:
        write('lastMsgAt', system.date.now())


def wire(peer_id, name, emoji, avatar=None):
    """A new data-channel opened with a peer — record in peers.<id>."""
    info = {
        'id':          peer_id,
        'name':        name,
        'emoji':       emoji,
        'avatar':      avatar,
        'state':       'open',
        'channels':    1,
        'connectedAt': system.date.now() if system else 0,
        'msgsIn':      0,
        'msgsOut':     0,
        'lastSeen':    system.date.now() if system else 0,
    }
    write('peers.' + peer_id, info)
    # bump room peerCount
    count = read('room.peerCount') or 1
    write('room.peerCount', count + 1)


def unwire(peer_id):
    """Data-channel with a peer closed — remove and decrement."""
    if system is not None:
        system.tag.deleteTags([_tag_path('peers.' + peer_id)])
    count = read('room.peerCount') or 1
    write('room.peerCount', max(1, count - 1))


def announce(trackers=None, n_offers=10):
    """Record an announce event against the current tracker."""
    inc('tracker.announces')
    if system is not None:
        write('tracker.lastAnnounceAt', system.date.now())


def on_offer(peer_id, offer_id):
    inc('signal.offersIn')
    _signal_last('offer', 'in', peer_id, offer_id)


def on_answer(peer_id, offer_id, direction):
    if direction == 'in':
        inc('signal.answersIn')
    else:
        inc('signal.answersOut')
    _signal_last('answer', direction, peer_id, offer_id)


def _signal_last(kind, direction, peer_id, offer_id):
    event = {
        'kind':    kind,
        'dir':     direction,
        'peerId':  peer_id,
        'offerId': offer_id,
        'ts':      system.date.now() if system else 0,
    }
    write('signal.last', event)


def join(room_name, room_hash):
    """A peer joined a room."""
    write('room.name', room_name)
    write('room.hash', room_hash)
    if system is not None:
        write('room.joinedAt', system.date.now())
    write('room.peerCount', 1)


# ---- namespace assertion --------------------------------------------

def owns(path):
    """True iff this provider is the authority for `path`."""
    for p in OWNED_PREFIXES:
        if path.startswith(p):
            return True
    return False
