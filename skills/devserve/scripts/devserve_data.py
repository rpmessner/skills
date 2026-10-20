"""Opt-in templates and conservative orphan cleanup, shared by both process backends."""
import hashlib
from pathlib import Path
import re
import tempfile


def comment(d, database):
    result = d.sql("SELECT COALESCE(shobj_description(oid, 'pg_database'), '') || '|' "
                   f"FROM pg_database WHERE datname = '{database}';")
    return None if not result else result[:-1]


def clone(d, database, source):
    if comment(d, source) is None:
        raise ValueError('template/source database does not exist; run base refresh first')
    if d.sql(f"SELECT count(*) FROM pg_stat_activity WHERE datname = '{source}';") != '0':
        raise ValueError('template/source has active connections; disconnect them or refresh with --dump')
    d.sql(f'CREATE DATABASE "{database}" TEMPLATE "{source}";')


def refresh(d, app, dump):
    if app['data'] != 'template' or not app.get('source_database'):
        raise ValueError('base refresh requires template data and source_database')
    base, source = app['template_database'], app['source_database']
    staging, retired = base + '_next', base + '_prev'
    mark = 'devserve:base:v1:' + app['name']
    current = comment(d, base)
    for name in (base, staging, retired):
        if comment(d, name) not in (None, mark):
            raise ValueError('refusing template database not created by devserve')
    for name in (staging, retired):
        if comment(d, name) == mark:
            d.sql(f'DROP DATABASE "{name}";')
    if dump:
        d.sql(f'CREATE DATABASE "{staging}";')
    else:
        clone(d, staging, source)
    d.sql(f"COMMENT ON DATABASE \"{staging}\" IS '{mark}';")
    try:
        if dump:
            with tempfile.TemporaryDirectory(prefix='devserve-base-') as root:
                path = str(Path(root) / 'data.dump')
                d.run(['pg_dump', '--format=custom', '--no-owner', '--no-acl', '--file', path, source])
                d.run(['pg_restore', '--exit-on-error', '--no-owner', '--no-acl', '--dbname', staging, path])
        # Transactional swap: never delete the previous base until its replacement is ready.
        swap = f'ALTER DATABASE "{staging}" RENAME TO "{base}";'
        if current is not None:
            swap = f'BEGIN; ALTER DATABASE "{base}" RENAME TO "{retired}"; {swap} COMMIT;'
        d.sql(swap)
    except BaseException:
        if comment(d, staging) == mark:
            d.sql(f'DROP DATABASE "{staging}";')
        raise
    d.sql(f'ALTER DATABASE "{base}" WITH ALLOW_CONNECTIONS false;')
    if current is not None:
        d.sql(f'DROP DATABASE "{retired}";')


def orphan_identity(app, database, mark):
    name = re.fullmatch(re.escape(app) + r'_preview_([a-z0-9_]{1,20})_([a-f0-9]{12})', database)
    if not name:
        return None
    unit = f'devserve-{app}-{name[1]}-{name[2]}.service'
    owner = re.fullmatch('devserve:v1:' + re.escape(unit) + ':([a-f0-9]{64})', mark)
    if not owner or not owner[1].startswith(name[2]):
        return None
    return unit, owner[1]


def gc(d, app, known, hashes, stopped, protected):
    output = d.sql("SELECT datname || '|' || shobj_description(oid, 'pg_database') FROM pg_database "
                   "WHERE shobj_description(oid, 'pg_database') LIKE 'devserve:v1:%';")
    for line in output.splitlines():
        database, mark = line.split('|', 1)
        identity = orphan_identity(app['name'], database, mark)
        if database in protected or not identity or identity[0] in known or (identity[1] in hashes and not stopped):
            continue
        # Unknown registry must not turn an active database into a forced drop.
        if d.sql(f"SELECT count(*) FROM pg_stat_activity WHERE datname = '{database}';") != '0':
            raise ValueError('orphan database has active connections; refusing cleanup')
        if comment(d, database) != mark:
            raise ValueError('orphan ownership changed; refusing cleanup')
        d.sql(f'DROP DATABASE "{database}";')


def worktree_hashes(d, app):
    output = d.run(['git', '-C', app['path'], 'worktree', 'list', '--porcelain', '-z'])
    paths = [item[len('worktree '):] for item in output.split('\0') if item.startswith('worktree ')]
    return [hashlib.sha256(str(Path(path).resolve()).encode()).hexdigest()
            for path in paths if Path(path).is_dir()]
