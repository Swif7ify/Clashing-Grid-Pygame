# Chain Reaction/network/client.py
import socket
import threading
import json
import sys

class Client:
    def __init__(self, game, action, server_ip):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(20)
        self.host = server_ip
        print(f"Connecting to server at {self.host}")
        self.port = 5555
        self.addr = (self.host, self.port)
        self.running = True
        self.game_state = None
        self.game = game
        self.player_role = None
        self.action = action
        threading.Thread(target=self.receive, daemon=True).start()
        self.connect()

    def connect(self):
        try:
            self.client.connect(self.addr)
            print("Connected to server")
            if self.action == "host":
                self.send({
                    "action": "host",
                    "rows": self.game.rows,
                    "cols": self.game.cols,
                    "expansion": self.game.expansion,
                    "advance_mode": self.game.advance_mode
                })
            else:
                self.send({"action": "join"})
        except (socket.error, socket.timeout) as e:
            print(f"Connection error: {e}")
            sys.exit()

    def send(self, data):
        """
        Sends JSON-encoded data to the server.

        :param data: dict
        """
        try:
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
                continue
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
        else:
            self.game_state = data
            self.game.update_state(self.game_state)