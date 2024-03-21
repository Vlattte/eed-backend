import asyncio
import websockets
import comparer
import json

import asyncio
import itertools
import json

import websockets
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse


app = FastAPI()


async def handler(websocket):

    message = await websocket.recv()
    print("message: ")
    print(message)
    event = json.loads(message)
    return_json = comparer.Comparer(event)
    print("[data for front]", return_json)
    await websocket.send(json.dumps(return_json, ensure_ascii=False))

@app.websocket('/')
async def main(websocket: WebSocket):
    print("SERVER ON")
    await websocket.accept()
    while True:
        message = await websocket.receive_json()
        return_json = comparer.Comparer(message)
        print("[data for front]", return_json)

        await websocket.send_json(return_json)
        # uvicor server:app --reload --port 8083

    # async with websockets.serve(handler, "", 8083, max_size=1000000):
    #     await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
