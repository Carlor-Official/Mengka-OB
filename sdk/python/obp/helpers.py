import aiohttp
def create_client_session(*args,**kwargs):
    return aiohttp.ClientSession(*args,**kwargs)
