"""Native loopback credential pages; the framework proxy supplies a service token."""
import asyncio, html, os, secrets
from aiohttp import web
from . import state
from .runtime import peer

_runner = None
_url = ''
_owners = {}
_locks = {}
_start_lock = asyncio.Lock()

def login_url(app, token):
    if not _url:
        raise RuntimeError('请在插件服务配置 public_base_url，并授予 expose_http 权限后重启插件')
    from urllib.parse import urlencode
    return _url + '/login?' + urlencode({'app': str(app), 'login': token})

async def start(context, modules):
    async with _start_lock:
        await _start(context, modules)

async def _start(context, modules):
    global _runner, _url
    candidates = [m for m in modules if callable(getattr(m, 'build_login_page', None)) and callable(getattr(m, 'complete_web_login', None))]
    if not candidates:
        return
    _owners[context.app_id] = (context, candidates[0])
    if _runner is not None or not state.configuration().get('public_base_url'):
        return

    async def login(request):
        if not secrets.compare_digest(request.headers.get('X-OB-Plugin-Token', ''), os.environ['OB_PLUGIN_TOKEN']):
            raise web.HTTPForbidden()
        app = request.query.get('app', '')
        owner = _owners.get(app)
        if owner is None:
            raise web.HTTPNotFound()
        ctx, module = owner
        token = request.query.get('login', '')
        if len(token) > 128:
            raise web.HTTPBadRequest()
        active = state.active_app.set(app)
        try:
            if request.method == 'GET':
                page = module.build_login_page(token)
                if page is None:
                    raise web.HTTPGone(text='登录链接已失效，请返回机器人重新申请。')
                import re
                page = re.sub(r'(<form\s+method="post"\s+action=)"[^"]*"', r'\1""', page)
                return web.Response(text=page, content_type='text/html')
            # Serialize all credential submissions per Bot so the same token cannot race.
            async with _locks.setdefault(app, asyncio.Lock()):
                form = dict(await request.post())
                if not secrets.compare_digest(str(form.get('login_token', '')), token):
                    raise web.HTTPForbidden()
                if module.build_login_page(token) is None:
                    raise web.HTTPGone(text='登录链接已失效。')
                try:
                    result = await module.complete_web_login(ctx, token, form)
                except Exception:
                    return web.Response(status=400, text='凭据验证失败，请核对填写内容或重新申请登录链接。')
                if result is None:
                    raise web.HTTPGone()
                return web.Response(text='验证成功，凭据已加密保存。可以关闭此页并返回机器人。', content_type='text/plain')
        finally:
            state.active_app.reset(active)

    app = web.Application(client_max_size=32*1024)
    app.router.add_get('/login', login)
    app.router.add_post('/login', login)
    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]
    try:
        result = await peer().call('expose_http', {'app_id': context.app_id, 'port': port})
    except BaseException:
        await runner.cleanup()
        raise
    _url = result['url']
    _runner = runner

async def close():
    global _runner, _url
    if _runner:
        await _runner.cleanup()
    _runner = None
    _url = ''
    _owners.clear()
    _locks.clear()
