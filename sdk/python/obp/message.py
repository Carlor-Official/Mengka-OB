from __future__ import annotations
from types import SimpleNamespace

def record(value, defaults=None):
    data=dict(defaults or {});data.update(value or {})
    return SimpleNamespace(**data)

class Message:
    def __init__(self,envelope,delivery_id=''):
        self.raw=envelope
        d=envelope.get('d') or {}
        self.id=str(d.get('id') or envelope.get('id') or '')
        self.content=str(d.get('content') or '').strip()
        self.display_content=self.content
        for mention in d.get('mentions') or []:
            if isinstance(mention,dict) and mention.get('bot') and mention.get('is_you'):
                identity=str(mention.get('member_openid') or mention.get('id') or '')
                if identity:
                    for text in (f'<@{identity}>',f'<@!{identity}>'):
                        self.content=self.content.replace(text,'').strip()
                        self.display_content=self.display_content.replace(text,'[@Bot]')
        self.event_id=str(envelope.get('id') or '')
        self.delivery_id=str(delivery_id)
        self.event_type=str(envelope.get('t') or '')
        a=d.get('author') or {}
        is_group=bool(d.get('group_openid') or d.get('group_id'))
        identity=(a.get('member_openid') or a.get('user_openid')) if is_group else (a.get('user_openid') or a.get('member_openid'))
        self.author=record(a,{'id':str(identity or ''),'member_openid':'','member_nickname':'','union_openid':'','user_openid':'','username':'','avatar':'','bot':False})
        self.group_openid=str(d.get('group_openid') or d.get('group_id') or '')
        self.union_group_openid=str(d.get('union_group_openid') or '')
        self.group=record({'id':self.group_openid,'group_openid':self.group_openid,'union_group_openid':self.union_group_openid}) if self.group_openid else None
        self.member_nickname=str(a.get('member_nickname') or '')
        self.guild_id=str(d.get('guild_id') or '')
        self.channel_id=str(d.get('channel_id') or '')
        self.member=record(d.get('member'),{'roles':[],'nick':'','user':self.author}) if d.get('member') else None
        self.timestamp=d.get('timestamp','')
        self.msg_type=d.get('msg_type',0)
        ext=(d.get('message_scene') or {}).get('ext',[])
        self.msg_idx=ext.get('msg_idx') if isinstance(ext,dict) else next((x[8:] for x in ext if isinstance(x,str) and x.startswith('msg_idx=')),None)
        self.mentions=d.get('mentions') or []
        self.attachments=d.get('attachments') or []
        # Keep official extensions intact, including picture cards and join requests.
        self.ark=d.get('ark')
        self.ark_type=d.get('ark_type','')
        self.card=d.get('card')
        self.join_request_id=d.get('join_request_id','')
        self.member_openid=d.get('member_openid','')
    @property
    def is_group(self):return bool(self.group_openid)
    @property
    def is_private(self):return self.event_type=='C2C_MESSAGE_CREATE'
