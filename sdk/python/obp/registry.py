"""Explicit privileged OBP registry capability, independent of framework files."""
from .state import active_app, configuration
from .runtime import peer

def call(op, **params):
    return peer().call_sync('registry_manage', {'app_id': active_app.get(), 'op': op, **params})

def snapshot():
    return call('snapshot')

def apply(value):
    return call('apply', snapshot=value)

def callback_base():
    from urllib.parse import urlsplit
    value = str(configuration().get('public_base_url') or '').rstrip('/')
    parsed = urlsplit(value)
    if parsed.scheme != 'https' or not parsed.netloc or parsed.path or parsed.query or parsed.fragment or parsed.username:
        raise ValueError('请配置本站 HTTPS public_base_url')
    return value + '/webhooks/official'
