import socket
import threading
import json
import sys

class Network:
    def __init__(self, game, action):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(10)  # Set a timeout for the socket
        self.host = "localhost"  # Server's IP address
        self.port = 5555
        self.addr = (self.host, self.port)
        self.running = True
        self.game_state = None  # Initialize game_state
        self.game = game  # Initialize game
        self.player_role = None  # Initialize player role
        self.action = action  # Store the action (host or join)
        threading.Thread(target=self.receive, daemon=True).start()
        self.connect()

    def connect(self):
        try:
            self.client.connect(self.addr)
            print("Connected to server")
            if self.action == "host":
                self.send({"action": "host"})
            else:
                self.send({"action": "join", "code": self.game.code})
        except (socket.error, socket.timeout) as e:
            print(f"Connection error: {e}")
            sys.exit()

    def send(self, data):
        """
        Sends JSON-encoded data to the server.

        :param data: dict
        """
        try:
            if "code" not in data:
                data["code"] = self.game.code  # Include the game code in the data if not already present
            self.client.send((json.dumps(data) + "\n").encode('utf-8'))
        except socket.error as e:
            print(f"Error sending data: {e}")

    def receive(self):
        buffer = ""
        while self.running:
            try:
                data = self.client.recv(2048).decode('utf-8')
                if data:
                    buffer += data
                    while "\n" in buffer:
                        message, buffer = buffer.split("\n", 1)
                        data = json.loads(message)
                        if "playerRole" in data:
                            self.player_role = data["playerRole"]
                            if "code" in data:
                                self.game.code = data["code"]
                            if "state" in data:
                                self.game.update_state(data["state"])
                            print(f"Assigned player role: {self.player_role}")
                        elif "error" in data:
                            print(f"Error: {data['error']}")
                            self.running = False
                        else:
                            print(f"Server update: {data}")
                            self.handle_server_update(data)
            except socket.timeout:
                continue  # Ignore timeouts and keep listening
            except socket.error as e:
                print(f"Error receiving data: {e}")
                self.running = False

    def handle_server_update(self, data):
        if "action" in data:
            if data["action"] == "player2_joined":
                print("Player 2 has joined the game.")
                self.game_state = data["state"]
                self.game.update_state(self.game_state)
            elif data["action"] == "initial_state":
                print("Game state received for Player 2.")
                self.game_state = data["state"]
                self.game.update_state(self.game_state)
            elif data["action"] == "sync_grid":
                # Handle grid synchronization for Player 2
                print("Grid synchronized with Player 1.")
                self.game_state = data["state"]
                self.game.update_state(self.game_state)
        else:
            # Update the local game state with the data received from the server
            self.game_state = data
            self.game.update_state(self.game_state)