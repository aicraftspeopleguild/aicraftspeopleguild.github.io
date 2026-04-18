# -*- coding: utf-8 -*-
#
# ACG · errors tag provider (Jython 2.7)
#
# Owns: errors.*
# Browser runtime: /js/errors.js
# Viewer page:     /controls/scada/gateway/gateway-log.html
# Location:        /controls/scada/errors/  (SCADA gateway area)
#
# Ring-buffer-backed log.  Every entry hits both a fixed-size list tag
# (errors.ring) and a monotonically-increasing counter (errors.count).
# Per-level counters live at errors.byLevel.<LEVEL>.count.
#
from __future__ import print_function, division, absolute_import

try:
    import system
except ImportError:
    system = None

NAMESPACE = 'errors'
RING_SIZE = 200
OWNED_PREFIXES = ('errors.',)
LEVELS = ('ERROR', 'WARN', 'INFO', 'DEBUG')


# local mirror in case the gateway is offline
_ring = []


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

def log_entry(level, logger, msg, meta=None):
    """Append a log entry; update ring + counters."""
    if level not in LEVELS:
        level = 'INFO'
    entry = {
        'ts':     system.date.now() if system else 0,
        'level':  level,
        'logger': str(logger or 'app'),
        'msg':    str(msg),
    }
    if meta and isinstance(meta, dict):
        if 'stack' in meta:
            entry['stack'] = meta['stack']
        rest = {k: v for k, v in meta.iteritems() if k != 'stack'}
        if rest:
            entry['meta'] = rest

    _ring.append(entry)
    while len(_ring) > RING_SIZE:
        _ring.pop(0)

    inc('count')
    inc('byLevel.%s.count' % level)
    write('last', entry)
    write('ring', list(_ring))
    if system is not None:
        write('lastAt', system.date.now())
    return entry


def error(logger, msg, meta=None):
    return log_entry('ERROR', logger, msg, meta)


def warn(logger, msg, meta=None):
    return log_entry('WARN', logger, msg, meta)


def info(logger, msg, meta=None):
    return log_entry('INFO', logger, msg, meta)


def debug(logger, msg, meta=None):
    return log_entry('DEBUG', logger, msg, meta)


def get_all():
    """Return a copy of the current ring."""
    return list(_ring)


def clear_all():
    del _ring[:]
    write('ring', [])
    write('count', 0)
    for lvl in LEVELS:
        write('byLevel.%s.count' % lvl, 0)


def owns(path):
    for p in OWNED_PREFIXES:
        if path.startswith(p):
            return True
    return False
