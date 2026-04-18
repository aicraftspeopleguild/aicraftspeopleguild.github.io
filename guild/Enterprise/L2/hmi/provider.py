# -*- coding: utf-8 -*-
#
# ACG · HMI tag provider (Jython 2.7)
#
# Owns: hmi.*
# Aligns with ISA-101 (layers, palette, faceplates). Full dense spec at
# /controls/docs/standards/konomi/isa101/.
#
from __future__ import print_function, division, absolute_import

try:
    import system
except ImportError:
    system = None

NAMESPACE = 'hmi'
OWNED_PREFIXES = ('hmi.',)
NAV_HISTORY_SIZE = 50

LAYERS = {
    'L1': {'name': 'Overview', 'scope': 'Plant/Site',    'info': 'KPIs,Status,Alarms',   'nav': ['L2']},
    'L2': {'name': 'Area',     'scope': 'Process Area',  'info': 'Flows,States,Trends',  'nav': ['L1', 'L3']},
    'L3': {'name': 'Unit',     'scope': 'Equipment',     'info': 'Faceplate,Control',    'nav': ['L2', 'L4']},
    'L4': {'name': 'Detail',   'scope': 'Diagnostic',    'info': 'Config,Tuning',        'nav': ['L3', 'L5']},
    'L5': {'name': 'Support',  'scope': 'Maintenance',   'info': 'Calibration,History',  'nav': ['L4']},
}

PALETTE = {
    'Normal':     {'hex': '#808080', 'use': 'default'},
    'Running':    {'hex': '#00AA00', 'use': 'active'},
    'Stopped':    {'hex': '#404040', 'use': 'inactive'},
    'Warning':    {'hex': '#FFCC00', 'use': 'attention'},
    'Alarm':      {'hex': '#CC0000', 'use': 'action required'},
    'Fault':      {'hex': '#CC0000', 'use': 'equipment fault'},
    'Maint':      {'hex': '#0066CC', 'use': 'out of service'},
    'Disabled':   {'hex': '#808080', 'use': 'n/a'},
    'Manual':     {'hex': '#FF6600', 'use': 'manual mode'},
    'Transition': {'hex': '#00CCCC', 'use': 'state changing'},
}

_nav_history = []
_faceplates = {}


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

def init():
    """Seed static catalogs (layers + palette) into the tag plant."""
    for lid, info in LAYERS.iteritems():
        payload = {'id': lid}
        payload.update(info)
        write('layers.%s' % lid, payload)
    for state, info in PALETTE.iteritems():
        payload = {'state': state}
        payload.update(info)
        write('palette.%s' % state, payload)
    write('alarms.summary.total', 0)
    write('alarms.summary.unacked', 0)
    for p in (1, 2, 3, 4):
        write('alarms.summary.p%d' % p, {'priority': p, 'count': 0, 'unacked': 0})


def goto(path, layer='L3'):
    """Record a navigation to `path` at ISA-101 layer `layer`."""
    entry = {
        'path':  str(path),
        'layer': layer if layer in LAYERS else 'L3',
        'ts':    system.date.now() if system else 0,
    }
    _nav_history.append(entry)
    while len(_nav_history) > NAV_HISTORY_SIZE:
        _nav_history.pop(0)
    write('nav.path', entry['path'])
    write('nav.history', list(_nav_history))
    write('layer.current', entry['layer'])
    return entry


def register_faceplate(tag, title, equipment=None, pv=None, sp=None, commands=None, nav=None):
    fp = {
        'tag':       str(tag),
        'title':     str(title),
        'equipment': equipment,
        'pv':        list(pv or []),
        'sp':        list(sp or []),
        'commands':  list(commands or []),
        'nav':       list(nav or []),
    }
    _faceplates[tag] = fp
    write('faceplates.%s' % tag, fp)
    return fp


def set_alarm_summary(priority, count, unacked):
    if priority not in (1, 2, 3, 4):
        return
    write('alarms.summary.p%d' % priority, {
        'priority': priority, 'count': int(count), 'unacked': int(unacked),
    })


def recompute_alarm_totals():
    total = 0
    unack = 0
    for p in (1, 2, 3, 4):
        row = read('alarms.summary.p%d' % p) or {}
        total += int(row.get('count', 0))
        unack += int(row.get('unacked', 0))
    write('alarms.summary.total', total)
    write('alarms.summary.unacked', unack)
    return total, unack


def get_faceplate(tag):
    return _faceplates.get(tag)


def clear_nav_history():
    del _nav_history[:]
    write('nav.history', [])
