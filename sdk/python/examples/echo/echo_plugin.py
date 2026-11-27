from obp.module import Module, on_event

class EchoPlugin(Module):
    @on_event("C2C_MESSAGE_CREATE", "GROUP_AT_MESSAGE_CREATE")
    async def echo(self, context, message):
        if message.content.strip() != "ping":
            return 0
        result = await context.reply(message, "pong")
        if isinstance(result, dict) and result.get("code"):
            raise RuntimeError(f"QQ rejected response: {result['code']}")
        return 1
