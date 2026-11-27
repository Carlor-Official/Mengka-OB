from .module import Module,on_event
from .state import configuration
from .runtime import peer

class ConsoleLogin(Module):
    name='控制台登录'
    priority=-10
    command='后台登录'
    kind='web'
    @on_event('GROUP_AT_MESSAGE_CREATE','GROUP_MESSAGE_CREATE','C2C_MESSAGE_CREATE')
    async def login(self,context,message):
        if message.content.strip()!=self.command:return 0
        if message.event_type!='C2C_MESSAGE_CREATE':
            await context.reply(message,'请在机器人私聊中申请登录，登录凭据不会发送到群里。');return 1
        actor=str(message.author.user_openid or message.author.id)
        admins=configuration().get('console_admin_ids',[])
        if actor not in admins:
            await context.reply(message,'你没有控制台登录权限。');return 1
        result=await peer().call('issue_login_ticket',{'app_id':context.app_id,'delivery_id':message.delivery_id,'kind':self.kind})
        text=f"萌卡OB 登录凭据（5分钟有效，仅可使用一次）\n用户名：{result['username']}\n在密码栏填写：{result['ticket']}"
        if configuration().get('login_scope')=='bot':text+='\n此凭据仅能管理当前机器人。'
        if configuration().get('console_login_url'):text+='\n'+str(configuration()['console_login_url'])
        if result.get('url'):text+='\n'+result['url']
        await context.reply(message,text)
        return 1
