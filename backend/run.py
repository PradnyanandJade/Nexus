import asyncio
import sys

import uvicorn


if sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )


async def main():
    config = uvicorn.Config(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        loop="asyncio",
    )

    server = uvicorn.Server(config)

    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())