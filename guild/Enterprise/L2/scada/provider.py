# -*- coding: utf-8 -*-
#
# ACG · SCADA tag provider (Jython 2.7)
#
# Owns: sys.*, version.*
#
# SCADA is itself a subsystem with a tag footprint (uptime, build sha,
# user-agent, etc.) and lives alongside /chat, /auth, /errors, /sandbox.
# Browser runtime: /js/main.js seeds these + /js/version.js polls
# GitHub commits.
#
from __future__ import print_function, division, absolute_import

try:
    import system
except ImportError:
    system = None

NAMESPACE = 'scada'
OWNED_PREFIXES = ('sys.', 'version.')


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

def seed_sys(my_id, my_nm, my_em, tracker_count, user_agent):
    write('sys.startedAt', system.date.now() if system else 0)
    write('sys.myId', my_id)
    write('sys.myNm', my_nm)
    write('sys.myEm', my_em)
    write('sys.trackerCount', tracker_count)
    write('sys.userAgent', user_agent)
    write('sys.uptimeSec', 0)


def tick_uptime():
    inc('sys.uptimeSec')


def publish_version(sha, committed_at, message, url):
    write('version.sha', sha)
    write('version.shortSha', sha[:7] if sha else None)
    write('version.committedAt', committed_at)
    write('version.message', message)
    write('version.url', url)


def owns(path):
    for p in OWNED_PREFIXES:
        if path.startswith(p):
            return True
    return False
