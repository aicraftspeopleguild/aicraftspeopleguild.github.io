# -*- coding: utf-8 -*-
#
# ACG · PLC tag provider (Jython 2.7)
#
# Owns: plc.*
# Backing store: /controls/plc/git/  (GitPLC UDT templates)
# Standard:      /controls/docs/standards/gitplc/
#
# This provider keeps a live mirror of the GitPLC project state in the
# tag plant. It does *not* parse vendor files itself - that is the job
# of the α (parse) / β (gen) agents described in the standard. It just
# publishes what the repo currently holds.
#
from __future__ import print_function, division, absolute_import

try:
    import system
except ImportError:
    system = None

NAMESPACE = 'plc'
OWNED_PREFIXES = ('plc.',)

TEMPLATE_ROOT = '/controls/plc/git/'
STANDARD_ROOT = '/controls/docs/standards/gitplc/'

VENDORS = ('ab', 'siemens', 'codesys', 'beckhoff', 'omron', 'mitsubishi')

_types = {}
_equipment = {}
_sync = {}


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

def set_project(name, vendor='universal', version='1.0.0', isa_level='Unit'):
    hdr = {
        'name':     str(name),
        'vendor':   vendor if vendor in VENDORS or vendor == 'universal' else 'universal',
        'version':  str(version),
        'isaLevel': isa_level,
    }
    write('project', hdr)
    return hdr


def register_type(name, base=None, version='1.0.0', fields=0, kind='udt'):
    row = {
        'name':    str(name),
        'base':    base,
        'version': str(version),
        'fields':  int(fields),
        'kind':    kind,
    }
    _types[name] = row
    write('types.%s' % name, row)
    write('types.count', len(_types))
    return row


def register_equipment(path, level='Unit', children=0, state=None, mode=None):
    node = {
        'path':     str(path),
        'level':    level,
        'children': int(children),
        'state':    state,
        'mode':     mode,
    }
    _equipment[path] = node
    write('equipment.%s' % path.replace('/', '.'), node)
    write('equipment.count', len(_equipment))
    return node


def set_io(cards, points):
    write('io.cards', int(cards))
    write('io.points', int(points))


def set_sync(vendor, mode='idle', target=None, ok=True):
    if vendor not in VENDORS:
        return
    row = {
        'vendor': vendor,
        'mode':   mode,
        'target': target,
        'ts':     system.date.now() if system else 0,
        'ok':     bool(ok),
    }
    _sync[vendor] = row
    write('sync.%s' % vendor, row)
    return row


def set_git_head(hash_, subject='', dirty=False):
    head = {
        'hash':    str(hash_)[:12],
        'subject': str(subject),
        'ts':      system.date.now() if system else 0,
        'dirty':   bool(dirty),
    }
    write('git.head', head)
    write('git.dirty', bool(dirty))
    return head


def get_type(name):
    return _types.get(name)


def get_equipment(path):
    return _equipment.get(path)
