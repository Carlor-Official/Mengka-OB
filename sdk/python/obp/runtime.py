from __future__ import annotations
import asyncio,base64,concurrent.futures,contextvars,hashlib,importlib,inspect,json,logging,os,re,sys,threading,uuid,time
from collections import defaultdict
from . import state
from .message import Message
from .module import Module

log=logging.getLogger('obp')
event_scope=contextvars.ContextVar('obp_event',default='')
event_sequence=contextvars.ContextVar('obp_sequence',default=None)
_peer=None
_contexts={}

class RPCError(RuntimeError):
    def __init__(self,message,official_response=None):
        super().__init__(message)
        self.official_response=official_response
        self.uncertain=any(part in str(message) for part in ('结果不确定','结果未知'))
        m=re.search(r'业务码\s+(\d+)',str(message));self.code=int(m[1]) if m else -1

class Peer:
    def __init__(self,loop):
        self.loop=loop;self.queue=asyncio.Queue();self.pending={};self.lock=threading.Lock();self.output_lock=threading.Lock();self.ready=concurrent.futures.Future();self.closed=False
    def send(self,value):
        data=json.dumps(value,ensure_ascii=False,separators=(',',':')).encode('utf-8')+b'\n'
        if len(data)>4*1024*1024:raise ValueError('OBP frame exceeds 4 MiB')
        with self.output_lock:sys.__stdout__.buffer.write(data);sys.__stdout__.buffer.flush()
    def start(self):
        self.send({'type':'hello','protocol':'obp/1','token':os.environ['OB_PLUGIN_TOKEN'],'event':'lifecycle'})
        threading.Thread(target=self._reader,daemon=True).start()
    def _reader(self):
        try:
            buffered=b''
            while True:
                while b'\n' not in buffered:
                    chunk=os.read(sys.stdin.fileno(),65536)
                    if not chunk:return
                    buffered+=chunk
                    if len(buffered)>4*1024*1024:raise ValueError('oversize IPC input')
                line,buffered=buffered.split(b'\n',1)
                if len(line)>4*1024*1024:raise ValueError('oversize IPC input')
                f=json.loads(line)
                if f.get('type')=='ping':self.send({'type':'pong','id':f.get('id')})
                elif f.get('type')=='hello.ok':
                    if not self.ready.done():self.ready.set_result(f['data'])
                elif f.get('type')=='action.result':
                    with self.lock:future=self.pending.pop(f.get('id'),None)
                    if future and not future.done():
                        if f.get('success'):future.set_result(f.get('data'))
                        else:future.set_exception(RPCError(f.get('error','IPC request failed'),f.get('official_response')))
                elif f.get('type')=='event':self.loop.call_soon_threadsafe(self.queue.put_nowait,f)
                elif f.get('type') in ('error','hello.reject'):log.error('Protocol error: %s',f.get('error'))
        except Exception:log.exception('IPC input failed')
        finally:
            self.closed=True
            with self.lock:
                for f in self.pending.values():
                    if not f.done():f.set_exception(ConnectionError('IPC closed'))
                self.pending.clear()
            try:self.loop.call_soon_threadsafe(self.queue.put_nowait,None)
            except RuntimeError:pass
    def request(self,action,params,request_id=None):
        if self.closed:raise ConnectionError('IPC closed')
        scope=event_scope.get()
        if request_id is None:
            digest=hashlib.sha256(json.dumps([action,params],sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:32]
            request_id=('event:'+scope+':'+digest) if scope else uuid.uuid4().hex
        future=concurrent.futures.Future()
        with self.lock:
            if request_id in self.pending:return self.pending[request_id]
            self.pending[request_id]=future
        try:self.send({'type':'action','id':request_id,'action':action,'params':params,'deadline':int((time.time()+35)*1000)})
        except Exception:
            with self.lock:self.pending.pop(request_id,None)
            raise
        return future
    async def call(self,action,params,request_id=None):
        return await asyncio.wait_for(asyncio.wrap_future(self.request(action,params,request_id)),35)
    def call_sync(self,action,params,request_id=None):return self.request(action,params,request_id).result(35)

def peer():
    if _peer is None:raise RuntimeError('IPC runtime is not initialized')
    return _peer

class BotContext:
    def __init__(self,app_id):
        self.app_id=str(app_id);self.api=OfficialAPI(self);self._plugins=[];self.uin=str(state.bot_config(app_id).get('uin') or '');self._seq=defaultdict(int)
    async def reply(self,message,content=None,**kwargs):
        if isinstance(content,dict):kwargs={**content,**kwargs};content=kwargs.pop('content',None)
        if message.group_openid:scope,target='group',message.group_openid
        elif message.channel_id:scope,target='channel',message.channel_id
        elif message.guild_id:scope,target='direct',message.guild_id
        else:scope,target='c2c',str(getattr(message.author,'user_openid','') or getattr(message.author,'id','') or (message.raw.get('d') or {}).get('user_openid',''))
        kwargs.setdefault('msg_id',message.id)
        return await self.api.send(scope,target,content,**kwargs)
    async def send_group_message(self,target,content=None,**kwargs):return await self.api.send('group',target,content,**kwargs)
    async def send_private_message(self,target,content=None,**kwargs):return await self.api.send('c2c',target,content,**kwargs)

class OfficialAPI:
    def __init__(self,context):self.context=context
    async def call(self,action,**params):
        """Invoke a documented OB action; bot scope cannot be overridden.

        Each action must be declared and granted in the plugin manifest. Payload
        fields follow QQ's official API, pagination fields are top-level params.
        """
        if 'app_id' in params:raise ValueError('app_id is bound to this context')
        return await self._call(action,**params)
    async def _call(self,action,**params):
        try:return await peer().call(action,{**params,'app_id':self.context.app_id})
        except RPCError as e:
            if e.code>0 and not e.uncertain:
                body=(e.official_response or {}).get('body')
                if isinstance(body,dict):return body
                return {'code':e.code,'message':str(e)}
            raise
    async def get_user_info(self,user_openid):
        """Return QQ's user profile and proactive-message preference unchanged."""
        return await self._call('get_user_info',user_openid=str(user_openid))
    async def get_panels(self,scope=None,cursor=None,limit=None):
        """Query command panels for a QQ scope; QQ validates supplied values."""
        params={k:v for k,v in {'scope':scope,'cursor':cursor,'limit':limit}.items() if v is not None}
        return await self._call('get_panels',**params)
    async def send(self,scope,target,content=None,**kwargs):
        payload={k:v for k,v in kwargs.items() if v is not None and k not in ('auto_escape','reply_to')}
        if content is not None:payload['content']=content
        if 'msg_type' not in payload:payload['msg_type']=2 if payload.get('markdown') else 8 if payload.get('card') else 7 if payload.get('media') else 0
        msg_id=payload.get('msg_id');key=(scope,str(target),msg_id)
        if msg_id and 'msg_seq' not in payload:
            sequences=event_sequence.get()
            if sequences is None:sequences=self.context._seq
            sequences[key]=sequences.get(key,0)+1;payload['msg_seq']=sequences[key]
        try:return await self._call('send_message',scope=scope,target=str(target),payload=payload)
        except asyncio.TimeoutError:raise RPCError('消息提交结果不确定：等待 IPC 回执超时，不能据此认定未发送') from None
    async def send_group_message(self,target,content=None,**kwargs):return await self.send('group',target,content,**kwargs)
    async def send_c2c_message(self,target,content=None,**kwargs):return await self.send('c2c',target,content,**kwargs)
    async def send_stream_message(self,target,**payload):
        """One C2C fragment. Caller preserves stream_msg_id/msg_seq and index.

        Never automatically replay a fragment after an uncertain outcome.
        """
        try:return await self._call('send_stream_message',scope='c2c',target=str(target),payload=payload)
        except asyncio.TimeoutError:raise RPCError('消息提交结果不确定：等待 IPC 回执超时，不能据此认定未发送') from None
    async def upload(self,scope,target,file_type,url=None,**kwargs):
        payload={'file_type':file_type,**kwargs}
        if url:payload['url']=url
        if payload.get('file_data'):
            from .assets import save_asset
            raw=base64.b64decode(payload.pop('file_data'),validate=True)
            payload['file_ref']=save_asset(raw,'bin')
        return await self._call('upload_media',scope=scope,target=str(target),payload=payload)
    async def upload_group_media(self,target,file_type,url=None,**kwargs):return await self.upload('group',target,file_type,url,**kwargs)
    async def upload_c2c_media(self,target,file_type,url=None,**kwargs):return await self.upload('c2c',target,file_type,url,**kwargs)
    async def put_interaction(self,interaction_id,code=0):return await self._call('ack_interaction',interaction_id=str(interaction_id),code=int(code))
    on_interaction_result=put_interaction

async def _run(module_name):
    global _peer
    _peer=Peer(asyncio.get_running_loop());_peer.start();hello=await asyncio.wait_for(asyncio.wrap_future(_peer.ready),10);state.configure(hello.get('config',{}))
    # A single-account service also scopes module-level caches/optional OCR assets.
    # Per-account services are used for imported production data and credentials.
    apps=hello.get('app_ids',[])
    import_scope=state.active_app.set(str(apps[0]) if len(apps)==1 else '')
    try:module=importlib.import_module(module_name)
    finally:state.active_app.reset(import_scope)
    classes=list(dict.fromkeys(v for _,v in inspect.getmembers(module,inspect.isclass) if issubclass(v,Module) and v is not Module and v.__module__==module.__name__))
    if not classes:raise RuntimeError('No native OBP modules exported')
    workers={};queues={};ready=set()
    async def worker(ctx,q):
        app_token=state.active_app.set(ctx.app_id)
        try:
            for cls in classes:ctx._plugins.append(cls())
            ctx._plugins.sort(key=lambda p:p.priority)
            for p in ctx._plugins:await p.on_load(ctx)
            from .web import start
            await start(ctx,ctx._plugins)
            ready.add(ctx.app_id)
            if len(ready)==len(hello.get('app_ids',[])):_peer.send({'type':'runtime.status','event':'ready'})
            log.info('IPC module ready app=%s handlers=%d',ctx.app_id,len(ctx._plugins))
            while True:
                f=await q.get()
                if f is None:break
                if state.completed(f['id']):_peer.send({'type':'event.ack','id':f['id'],'consumed':state.receipt_consumed(f['id'])});continue
                msg=Message(f['data'],f['id']);event=f.get('event') or msg.event_type
                if event=='GROUP_MESSAGE_CREATE' and any(m.get('is_you') for m in msg.mentions if isinstance(m,dict)):event='GROUP_AT_MESSAGE_CREATE'
                token=event_scope.set(f['id'])
                sequence_token=event_sequence.set({})
                try:
                    stopped=False
                    for p in ctx._plugins:
                        if stopped and p.priority>=0:continue
                        if await p.handle_event(ctx,event,msg)==1:stopped=True
                    state.complete(f['id'],stopped);_peer.send({'type':'event.ack','id':f['id'],'consumed':stopped})
                except Exception:log.exception('Event handling failed app=%s type=%s',ctx.app_id,event)
                finally:event_scope.reset(token);event_sequence.reset(sequence_token)
        except Exception:
            _peer.send({'type':'runtime.status','event':'error'})
            log.exception('Module lifecycle failed app=%s',ctx.app_id)
            raise
        finally:
            for p in reversed(ctx._plugins):
                try:await asyncio.wait_for(p.on_unload(ctx),10)
                except Exception:log.exception('Module shutdown failed')
            state.active_app.reset(app_token)
    for app in hello.get('app_ids',[]):
        ctx=BotContext(app);_contexts[str(app)]=ctx;queues[str(app)]=asyncio.Queue(maxsize=256);workers[str(app)]=asyncio.create_task(worker(ctx,queues[str(app)]))
    log.info('OBP IPC process ready authorized_bots=%d',len(workers))
    from .assets import start_asset_maintenance
    asset_maintenance=start_asset_maintenance()
    incoming=None
    try:
        if not workers:_peer.send({'type':'runtime.status','event':'ready'})
        while True:
            incoming=asyncio.create_task(_peer.queue.get())
            done,_=await asyncio.wait([incoming,*workers.values()],return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                if task is not incoming:
                    await task
                    raise RuntimeError('Bot worker exited unexpectedly')
            f=await incoming
            if f is None:break
            q=queues.get(str(f.get('app_id')))
            if q is not None:q.put_nowait(f)
    finally:
        asset_maintenance.close()
        if incoming and not incoming.done():incoming.cancel()
        for task in workers.values():task.cancel()
        await asyncio.gather(*workers.values(),return_exceptions=True)
        from .web import close
        await close()

def run(module_name):
    if os.environ.get('OB_PLUGIN_PROTOCOL')!='obp/1' or os.environ.get('OB_PLUGIN_TRANSPORT')!='ipc':raise RuntimeError('Start through Mengka OB IPC')
    logging.basicConfig(level=logging.INFO,stream=sys.stderr,format='%(levelname)s %(name)s %(message)s')
    sys.stdout=sys.stderr
    asyncio.run(_run(module_name))
