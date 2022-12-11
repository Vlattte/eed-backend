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
        cmp_exit_code = comparer.Comparer("test", event)
        if cmp_exit_code == "RIGHT STEP":
            return_json = {
                "id": 1001,
                "next_id": 1017,
                "flag": False
            }
        else:
            return_json = {
                "flag": False
            }

        await websocket.send(json.dumps(return_json))
        print(cmp_exit_code)




async def main():
    print("SERVER ON")
    async with websockets.serve(echo, "localhost", 8080):
        await asyncio.Future()  # run forever

asyncio.run(main())
