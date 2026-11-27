from __future__ import annotations
import inspect
from .state import read_settings

def on_event(*events):
    def decorate(fn):
        fn.obp_events=tuple(events)
        return fn
    return decorate

class Module:
    name='OB module'
    priority=0
    def __init__(self):
        self._handlers={}
        for _,fn in inspect.getmembers(self,callable):
            for event in getattr(fn,'obp_events',()):self._handlers.setdefault(event,[]).append(fn)
    async def on_load(self,context):pass
    async def on_unload(self,context):pass
    async def handle_event(self,context,event,message):
        for fn in self._handlers.get(event,[]):
            if await fn(context,message)==1:return 1
        return 0
