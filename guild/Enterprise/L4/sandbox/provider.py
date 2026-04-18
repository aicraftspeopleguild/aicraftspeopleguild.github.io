# -*- coding: utf-8 -*-
#
# ACG · sandbox tag provider (Jython 2.7)
#
# Owns: sandbox.*
# Browser bridge: /js/sandbox-bridge.js  (subscribes to BroadcastChannel
#                                         "acg-mesh" and folds envelopes
#                                         into sandbox.<source>.*)
#
# Canonical envelope (§4):  {source, type, path?, value?, ts, ...}
#
from __future__ import print_function, division, absolute_import

try:
    import system
except ImportError:
    system = None

NAMESPACE = 'sandbox'
CHANNEL = 'acg-mesh'
OWNED_PREFIXES = ('sandbox.',)


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


# ---- bridge ingest ---------------------------------------------------

def on_envelope(env):
    """Called by the gateway message handler for each BroadcastChannel
    relay.  Mirrors sandbox tag writes into sandbox.<source>.<path>
    and bumps per-event counters for non-tag envelopes."""
    if not isinstance(env, dict):
        return
    source = env.get('source')
    etype = env.get('type')
    if not source or not etype:
        return
    base = 'sandbox.%s' % source
    if system is not None:
        write(base + '.lastEventAt', system.date.now())
    write(base + '.lastEvent', etype)

    if etype == 'tag' and env.get('path'):
        key = base + '.' + env['path']
        write(key, env.get('value'))
    else:
        write(base + '.event.' + etype, env)
        inc(base + '.events.' + etype + '.count')


def start():
    """Gateway startup hook — open the channel listener."""
    write('bridgeOpen', True)
    write('channel', CHANNEL)


def stop():
    write('bridgeOpen', False)


def owns(path):
    for p in OWNED_PREFIXES:
        if path.startswith(p):
            return True
    return False
