import asyncio
import websockets
import json
import threading

class Network:
    def __init__(self, host='ws://127.0.0.1:5555'):
        # Once you deploy to Render, change this host to: 
        # 'wss://your-service-name.onrender.com'
        self.host = host
        self.connected = False
        self.msg_queue = []
        self.loop = asyncio.new_event_loop()
        self.ws = None

    def connect(self):
        try:
            threading.Thread(target=self._start_event_loop, daemon=True).start()
            # Wait a moment for connection handshake
            import time
            time.sleep(1)
            return self.connected
        except Exception as e:
            print(f"Network startup error: {e}")
            return False

    def _start_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._listen())

    async def _listen(self):
        try:
            async with websockets.connect(self.host) as websocket:
                self.ws = websocket
                self.connected = True
                print("Connected to server via WebSockets")
                async for message in websocket:
                    data = json.loads(message)
                    self.msg_queue.append(data)
        except Exception as e:
            print(f"WebSocket connection error: {e}")
        finally:
            self.connected = False

    def send(self, data):
        if self.connected and self.ws:
            # Schedule the send in the background loop
            asyncio.run_coroutine_threadsafe(
                self.ws.send(json.dumps(data)), 
                self.loop
            )
