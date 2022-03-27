from fastapi import FastAPI,WebSocket
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from asyncio import Queue

app = FastAPI()

queue: Queue = None
teams: Queue = None

# creating the pydentic model
class Team(BaseModel):
  name:str
  uid:str

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def get():
    # print("Hiiiiii")
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

# this class is created to broadcast message to limited number of people
# class ConnectionManager2:
#     def __init__(self):
#         self.connections: dict[str, List[WebSocket]] = {}

#     async def connect(self, websocket: WebSocket,uid: str):
#         await websocket.accept()
#         print("ohoooo")
#         if uid in self.connections:
#           self.connections[uid].append(websocket)
#         else:
#           self.connections[uid] = [websocket]

#     async def broadcast(self, data: dict, uid: str):
#         for connection in self.connections[uid]:
#             await connection.send_json(data)


manager = ConnectionManager()
# manager2 = ConnectionManager2()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    while True:
        data = await websocket.receive_json()
        await manager.broadcast(data)

# @app.websocket("/cold/{client_id}")
# async def websocket_endpoint9(websocket: WebSocket, client_id: str):
#     await manager2.connect(websocket, client_id)
#     while True:
#         data = await websocket.receive_json()
#         await manager2.broadcast(data, client_id)

@app.websocket("/wsnew")
async def websocket_endpoint5(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

@app.websocket("/wscool")
async def websocket_endpoint7(websocket: WebSocket):
    await websocket.accept()
    global queue
    queue = Queue()
    while True:
        msg = await queue.get()
        await websocket.send_json({"message": msg})

# with this code we can trigger websocket when certain api is called
@app.get("/name/{name}")
async def on_mqtt_message(name:str):
    if queue:
      await queue.put(name)
    return {"success":"true"}

@app.post("/addteam")
async def addTeam(name:Team):
  if teams:
    await teams.put(name)
  return {"success":"true"}

# we would needing db to store teams I guess...
@app.websocket("/getteams")
async def streamTeam(websocket: WebSocket):
  await websocket.accept()
  global teams
  teams = Queue()
  while True:
    msg = await teams.get()
    await websocket.send_json({"team":msg.name,"uid":msg.uid})

# @app.websocket("/isjoined")
# async def isJoined(websocket: Websocket):
#   await websocket.accept()
