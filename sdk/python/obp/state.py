from __future__ import annotations
import contextlib, contextvars, json, os, sqlite3, threading
from pathlib import Path
from cryptography.fernet import Fernet

active_app = contextvars.ContextVar('obp_app_id', default='')
_config = {}
_lock = threading.RLock()
_cipher = None

def configure(config):
    global _config
    _config = dict(config or {})

def root() -> Path:
    value = os.environ.get('OB_PLUGIN_DATA_DIR')
    if not value:
        raise RuntimeError('OB_PLUGIN_DATA_DIR is required; refusing package-directory writes')
    p = Path(value).resolve(); p.mkdir(parents=True, exist_ok=True)
    return p

def data_path(module: str, name: str='') -> Path:
    p = root() / module
    app=active_app.get()
    if app:
        if not app.isdigit():raise ValueError('invalid Bot AppID')
        p=p/'bots'/app
    p.mkdir(parents=True, exist_ok=True)
    return p / name if name else p

@contextlib.contextmanager
def _db():
    c=sqlite3.connect(root()/'settings.sqlite3',timeout=20)
    c.execute('CREATE TABLE IF NOT EXISTS settings(app TEXT NOT NULL,module TEXT NOT NULL,value BLOB NOT NULL,PRIMARY KEY(app,module))')
    c.execute('CREATE TABLE IF NOT EXISTS receipts(id TEXT PRIMARY KEY,completed INTEGER NOT NULL DEFAULT 0)')
    if 'consumed' not in {r[1] for r in c.execute('PRAGMA table_info(receipts)')}:
        c.execute('ALTER TABLE receipts ADD COLUMN consumed INTEGER NOT NULL DEFAULT 0')
    try:
        with c:yield c
    finally:c.close()

def _fernet():
    global _cipher
    if _cipher is None:
        p=root()/'settings.key'
        if not p.exists():
            with p.open('xb') as f:f.write(Fernet.generate_key())
            p.chmod(0o600)
        _cipher=Fernet(p.read_bytes())
    return _cipher

def read_settings_sync(app, module):
    with _lock, _db() as c:
        base=dict(_config.get('settings',{}))
        base.update((_config.get('bots',{}).get(str(app),{}) or {}).get('settings',{}))
        row=c.execute('SELECT value FROM settings WHERE app=? AND module=?',(str(app),module)).fetchone()
        if row:base.update(json.loads(_fernet().decrypt(row[0])))
        return base

async def read_settings(app,module):
    return read_settings_sync(app,module)

def mutate_settings(app,module,mutation):
    with _lock, _db() as c:
        c.execute('BEGIN IMMEDIATE')
        row=c.execute('SELECT value FROM settings WHERE app=? AND module=?',(str(app),module)).fetchone()
        state=json.loads(_fernet().decrypt(row[0])) if row else {}
        result=mutation(state)
        cipher=_fernet().encrypt(json.dumps(state,ensure_ascii=False).encode())
        c.execute('INSERT INTO settings VALUES(?,?,?) ON CONFLICT(app,module) DO UPDATE SET value=excluded.value',(str(app),module,cipher))
        return result

def bot_config(app):
    return dict(_config.get('bots',{}).get(str(app),{}))

def configuration():return _config

def completed(event_id):
    with _lock, _db() as c:return bool(c.execute('SELECT 1 FROM receipts WHERE id=? AND completed=1',(event_id,)).fetchone())

def receipt_consumed(event_id):
    with _lock, _db() as c:
        row=c.execute('SELECT consumed FROM receipts WHERE id=? AND completed=1',(event_id,)).fetchone()
        return bool(row and row[0])

def complete(event_id,consumed=False):
    with _lock, _db() as c:c.execute('INSERT INTO receipts(id,completed,consumed) VALUES(?,1,?) ON CONFLICT(id) DO UPDATE SET completed=1,consumed=excluded.consumed',(event_id,int(consumed)))
