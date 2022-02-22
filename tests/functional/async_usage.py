import asyncio


async def unnessecary_await():
    return asyncio.sleep(10)
