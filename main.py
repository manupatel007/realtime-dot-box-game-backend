from fastapi import FastAPI,WebSocket
from typing import List

app = FastAPI()

html = ""
with open('index.html', 'r') as f:
    html = f.read()

@app.get("/")
async def get():
    return {"success":"true"}

class ConnectionManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    async def broadcast(self, data: dict):
        for connection in self.connections:
            await connection.send_json(data)


manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    while True:
        data = await websocket.receive_json()
        await manager.broadcast(data)
