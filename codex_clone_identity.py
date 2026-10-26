#!/usr/bin/env python3
"""Scoped clone identity reset. No network calls, no server revocation."""
import argparse, datetime, hashlib, json, os, pathlib, plistlib, shutil, sqlite3, subprocess, time
ROOT = pathlib.Path.cwd() / 'recovery-local'
HOME = pathlib.Path(os.environ.get('CODEX_HOME', str(pathlib.Path.home() / '.codex'))).expanduser().absolute()
INSTALL = ENV = SERVER = None
TARGET = ()
KEYS = ('electron-local-remote-control-installation-id', 'electron-local-remote-control-environment-id')
WHERE = 'websocket_url=? AND account_id=? AND app_server_client_name=? AND server_id=? AND environment_id=?'

def blockers():
    found = []
    for line in subprocess.check_output(['/bin/ps', '-axo', 'pid=,comm='], text=True).splitlines():
        fields = line.strip().split(None, 1)
        if len(fields) != 2:
            continue
        pid, comm = fields
        name = pathlib.Path(comm).name.lower()
        if any((part in comm for part in ('/Applications/ChatGPT.app/Contents/', '/Applications/Codex.app/Contents/'))) or name in ('codex', 'codex-app-server', 'codex-app-server-daemon'):
            if name != 'browser_crashpad_handler':
                found.append(line.strip())
    return found

def validate(root=HOME):
    if not not root.is_symlink():
        raise RuntimeError('CODEX_HOME must not be a symlink')
    paths = [root / 'installation_id', root / '.codex-global-state.json', root / '.codex-global-state.json.bak', root / 'state_5.sqlite']
    for p in paths:
        if not (p.is_file() and (not p.is_symlink())):
            raise RuntimeError(f'Unexpected path: {p}')
    if not (root / 'installation_id').read_text().strip() == INSTALL:
        raise RuntimeError('Installation changed; stop and recheck')
    for p in paths[1:3]:
        d = json.loads(p.read_text())
        if not (d.get(KEYS[0]) == INSTALL and d.get(KEYS[1]) == ENV):
            raise RuntimeError(f'Identity changed: {p}')
    c = sqlite3.connect((root / 'state_5.sqlite').as_uri() + '?mode=ro', uri=True)
    try:
        if not c.execute('SELECT count(*) FROM remote_control_enrollments WHERE ' + WHERE, TARGET).fetchone()[0] == 1:
            raise RuntimeError('Expected exactly one target registration')
    finally:
        c.close()
    return paths

def atomic(p, data, mode):
    tmp = p.with_name(p.name + '.clone-reset-tmp')
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, p)
    finally:
        if tmp.exists():
            tmp.unlink()

def other_content_digest(c):
    h = hashlib.sha256()
    for name, sql in c.execute("SELECT name,sql FROM sqlite_master WHERE type='table' AND name!='remote_control_enrollments' ORDER BY name").fetchall():
        h.update(repr((name, sql)).encode())
        escaped = name.replace('"', '""')
        for row in c.execute('SELECT * FROM "' + escaped + '"'):
            h.update(repr(row).encode())
    return h.hexdigest()

def reset(root=HOME, output=ROOT, guard=True):
    if guard:
        if not not blockers():
            raise RuntimeError('Codex is still running')
    paths = validate(root)
    stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
    backup = output / ('backup-after-exit-' + stamp)
    backup.mkdir(mode=448)
    saved = {p: (p.read_bytes(), p.stat().st_mode & 511) for p in paths if p.name != 'state_5.sqlite'}
    for p, (data, mode) in saved.items():
        q = backup / p.name
        q.write_bytes(data)
        q.chmod(384)
    for name in ('config.toml', 'auth.json'):
        p = root / name
        if p.is_file():
            q = backup / name
            shutil.copyfile(p, q)
            q.chmod(384)
    src = sqlite3.connect((root / 'state_5.sqlite').as_uri() + '?mode=ro', uri=True)
    dst = sqlite3.connect(backup / 'state_5.sqlite')
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()
    (backup / 'state_5.sqlite').chmod(384)
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in backup.iterdir() if p.is_file()}
    (backup / 'sha256.json').write_text(json.dumps(hashes, indent=2))
    c = sqlite3.connect(root / 'state_5.sqlite', timeout=2)
    moved = False
    modified = []
    try:
        if guard:
            if not not blockers():
                raise RuntimeError('Codex restarted during backup')
        for p, (data, mode) in saved.items():
            if not p.read_bytes() == data:
                raise RuntimeError(f'Concurrent file change: {p}')
        c.execute('BEGIN EXCLUSIVE')
        if not c.execute('SELECT count(*) FROM remote_control_enrollments WHERE ' + WHERE, TARGET).fetchone()[0] == 1:
            raise RuntimeError('Precondition failed')
        before = other_content_digest(c)
        oldrows = c.execute('SELECT * FROM remote_control_enrollments').fetchall()
        cur = c.execute('DELETE FROM remote_control_enrollments WHERE ' + WHERE, TARGET)
        if not cur.rowcount == 1:
            raise RuntimeError('Precondition failed')
        if not c.execute('SELECT * FROM remote_control_enrollments').fetchall() == [r for r in oldrows if not (r[0:3] == TARGET[0:3] and r[3] == SERVER and (r[4] == ENV))]:
            raise RuntimeError('Precondition failed')
        if not other_content_digest(c) == before:
            raise RuntimeError('Unrelated table content changed')
        for p in paths[1:3]:
            original = json.loads(saved[p][0])
            updated = {k: v for k, v in original.items() if k not in KEYS}
            atomic(p, (json.dumps(updated, ensure_ascii=False, separators=(',', ':')) + '\n').encode(), saved[p][1])
            modified.append(p)
            if not json.loads(p.read_text()) == updated:
                raise RuntimeError('Precondition failed')
            if not json.loads(p.read_text()).get('electron-remote-control-client-enrollments') == original.get('electron-remote-control-client-enrollments'):
                raise RuntimeError('Precondition failed')
        os.rename(root / 'installation_id', backup / 'installation_id.moved')
        moved = True
        if guard:
            if not not blockers():
                raise RuntimeError('Codex restarted during reset')
        c.commit()
    except BaseException:
        c.rollback()
        for p in modified:
            atomic(p, saved[p][0], saved[p][1])
        if moved:
            os.rename(backup / 'installation_id.moved', root / 'installation_id')
        raise
    finally:
        c.close()
    result = {'status': 'local_reset_complete_registration_pending', 'time': stamp, 'backup': str(backup), 'removed_host_registration_count': 1, 'unrelated_tables_sha256': before, 'client_enrollments_preserved': True, 'new_ids_generated_by_script': False, 'next': 'Restart Codex and enable remote connection; verify new installation/environment/server IDs.'}
    (output / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return result

def select_app():
    candidates = [pathlib.Path('/Applications/ChatGPT.app'), pathlib.Path('/Applications/Codex.app')]
    found = []
    for app in candidates:
        plist = app / 'Contents/Info.plist'
        if plist.exists():
            with plist.open('rb') as f:
                info = plistlib.load(f)
            if info.get('CFBundleIdentifier') == 'com.openai.codex':
                found.append((app, info))
    if len(found) != 1:
        raise RuntimeError('Expected one Codex application in /Applications; inspect manually')
    return found[0]

def inspect_plan(root, account_id=None):
    installation = (root / 'installation_id').read_text().strip()
    state = json.loads((root / '.codex-global-state.json').read_text())
    db = sqlite3.connect((root / 'state_5.sqlite').as_uri() + '?mode=ro', uri=True)
    try:
        rows = db.execute('SELECT websocket_url,account_id,app_server_client_name,server_id,environment_id FROM remote_control_enrollments').fetchall()
    finally:
        db.close()
    rows = [r for r in rows if r[2] == 'Codex Desktop' and (account_id is None or r[1] == account_id)]
    if len(rows) != 1:
        raise RuntimeError('Expected exactly one Codex Desktop host registration; select --account-id or inspect manually')
    row = rows[0]
    if state.get(KEYS[0]) != installation or state.get(KEYS[1]) != row[4]:
        raise RuntimeError('JSON, installation file and database disagree; inspect manually')
    app, info = select_app()
    return {'schema': 1, 'codex_home': str(root), 'app_path': str(app), 'app_build': info['CFBundleVersion'], 'installation_id': installation, 'target': list(row)}

def configure(plan):
    global HOME, INSTALL, ENV, SERVER, TARGET
    if plan.get('schema') != 1 or len(plan.get('target', [])) != 5:
        raise RuntimeError('Invalid plan schema')
    HOME = pathlib.Path(plan['codex_home']).expanduser().absolute()
    INSTALL = plan['installation_id']
    TARGET = tuple(plan['target'])
    SERVER, ENV = TARGET[3:5]

def main():
    p = argparse.ArgumentParser(description='Inspect or reset cloned Codex host registration. macOS only; no network requests.')
    p.add_argument('--home', type=pathlib.Path, default=HOME)
    p.add_argument('--account-id', help='Select a host registration when multiple accounts exist')
    p.add_argument('--plan-out', type=pathlib.Path, help='Write a private local plan; does not reset anything')
    p.add_argument('--plan', type=pathlib.Path, help='Use the previously reviewed local plan')
    p.add_argument('--apply', action='store_true', help='Reset local host identity after application exit')
    p.add_argument('--wait-for-exit', action='store_true')
    p.add_argument('--output', type=pathlib.Path, default=ROOT, help='Private backup and result directory')
    a = p.parse_args()
    if a.apply and a.plan is None:
        p.error('--apply requires --plan; inspect and review the local plan first')
    if a.plan is not None:
        plan = json.loads(a.plan.read_text())
    else:
        plan = inspect_plan(a.home.expanduser().absolute(), a.account_id)
    configure(plan)
    validate(HOME)
    if a.plan_out:
        fd = os.open(a.plan_out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 384)
        with os.fdopen(fd, 'w') as f:
            json.dump(plan, f, indent=2)
    print(json.dumps(plan, indent=2), flush=True)
    if not a.apply:
        print('READ ONLY. These identifiers are private; do not publish this output.')
        print('Process blockers:', len(blockers()))
        return
    app, info = select_app()
    if str(app) != plan['app_path'] or info['CFBundleVersion'] != plan['app_build']:
        raise RuntimeError('Application changed since inspection')
    if str(info['CFBundleVersion']) != '21828':
        raise RuntimeError('Apply supported only for inspected build 21828; re-audit other versions')
    output = a.output.expanduser().absolute()
    if output.exists() and output.is_symlink():
        raise RuntimeError('Output must not be a symlink')
    output.mkdir(mode=448, parents=True, exist_ok=True)
    output.chmod(448)
    import fcntl
    with (output / '.reset.lock').open('a') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        if a.wait_for_exit:
            print('Waiting up to 30 minutes. Quit Codex and other Codex CLI processes. Ctrl-C cancels.', flush=True)
            end = time.monotonic() + 1800
            quiet = 0
            while time.monotonic() < end:
                quiet = 0 if blockers() else quiet + 1
                if quiet >= 5:
                    break
                time.sleep(2)
            else:
                raise RuntimeError('Timed out; no reset performed')
        reset(HOME, output, guard=True)
if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, ValueError, sqlite3.Error) as e:
        raise SystemExit('STOP: ' + str(e))
