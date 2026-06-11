import asyncio
from src import config as C
import src.github_utils as gu

async def main():
    try:
        res = await gu._graphql("query { viewer { login } }", {}, C.GH_TOKEN)
        print("RESULT", res)
    except Exception as e:
        print("ERROR:", e)

asyncio.run(main())
