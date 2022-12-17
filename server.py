import asyncio
import websockets
import comparer
import json

import asyncio
import itertools
import json

import websockets


async def echo(websocket):
    async for message in websocket:

        event = json.loads(message)
        return_json = comparer.Comparer("P302O", event)
        await websocket.send(json.dumps(return_json))




async def main():
    print("SERVER ON")
    async with websockets.serve(echo, "localhost", 8080):
        await asyncio.Future()  # run forever

asyncio.run(main())
