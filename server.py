import asyncio
import websockets
import json
import os

class ChessServer:
    def __init__(self):
        self.rooms = {} # {code: [ws1, ws2]}

    async def handle_client(self, websocket):
        print(f"New connection established")
        room_code = None
        
        try:
            async for message in websocket:
                data = json.loads(message)
                cmd = data.get("cmd")
                code = data.get("code")

                if cmd == "create":
                    room_code = code
                    self.rooms[code] = [websocket]
                    print(f"Room {code} created")
                
                elif cmd == "join":
                    if code in self.rooms and len(self.rooms[code]) == 1:
                        room_code = code
                        self.rooms[code].append(websocket)
                        # Notify both players
                        await self.rooms[code][0].send(json.dumps({"type": "start", "color": "white"}))
                        await self.rooms[code][1].send(json.dumps({"type": "start", "color": "black"}))
                        print(f"Room {code} joined. Match started.")
                    else:
                        await websocket.send(json.dumps({"type": "error", "msg": "Room full or not found"}))

                else:
                    # Relay any other command (move, resign, reset, etc.)
                    if room_code in self.rooms:
                        # Relay to everyone in the room except the sender
                        for client in self.rooms[room_code]:
                            if client != websocket:
                                await client.send(message)
        except Exception as e:
            print(f"Connection error: {e}")
        finally:
            # Cleanup on disconnect
            if room_code in self.rooms:
                if websocket in self.rooms[room_code]:
                    self.rooms[room_code].remove(websocket)
                if not self.rooms[room_code]:
                    del self.rooms[room_code]
            print(f"Connection closed for room {room_code}")

async def main():
    server = ChessServer()
    # Render provides the port in the PORT environment variable
    port = int(os.environ.get("PORT", 5555))
    print(f"Server starting on port {port}...")
    async with websockets.serve(server.handle_client, "0.0.0.0", port):
        await asyncio.Future() # run forever

if __name__ == "__main__":
    asyncio.run(main())
