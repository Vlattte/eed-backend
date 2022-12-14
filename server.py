import asyncio
import websockets
import comparer
import json

import asyncio
import itertools
import json

import websockets


async def handler(websocket):
    try:
        message = await websocket.recv()
        event = json.loads(message)
        return_json = comparer.Comparer("P302O", event)
        await websocket.send(json.dumps(return_json, ensure_ascii=False))
    except:
        print("NOTHING")


async def main():
    print("SERVER ON")
    async with websockets.serve(handler, "", 8080):
        await asyncio. Future()

if __name__ == "__main__":
    asyncio.run(main())
