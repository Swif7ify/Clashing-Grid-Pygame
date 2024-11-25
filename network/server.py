import socket
import threading
import json
import random

class Server:
    def __init__(self, host="127.0.0.1", port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        print("Server started on", host, ":", port)

        self.connections = []
        self.game_state = {"grid": [[None for _ in range(6)] for _ in range(6)], "playerTurn": 1}
        self.player_roles = {}  # Dictionary to store player roles
        self.game_codes = {}  # Dictionary to store game codes and their connections

        self.lock = threading.Lock()

    def broadcast(self, data, game_code):
        message = json.dumps(data) + "\n"
        for conn in self.game_codes[game_code]:
            try:
                conn.send(message.encode('utf-8'))
            except socket.error:
                self.game_codes[game_code].remove(conn)

    def handle_client(self, conn, addr):
        print(f"New connection from {addr}")

        while True:
            try:
                data = conn.recv(2048).decode('utf-8')
                if not data:
                    break

                with self.lock:
                    data = json.loads(data)
                    if data["action"] == "host":
                        game_code = str(random.randint(10000, 99999))
                        self.game_codes[game_code] = [conn]
                        self.player_roles[conn] = 1
                        self.game_state = {"grid": [[None for _ in range(6)] for _ in range(6)], "playerTurn": 1}
                        self.game_state["grid"][2][1] = 1
                        self.game_state["grid"][2][4] = 2
                        conn.send((json.dumps({"playerRole": 1, "code": game_code}) + "\n").encode('utf-8'))
                    elif data["action"] == "join":
                        game_code = data["code"]
                        if game_code in self.game_codes and len(self.game_codes[game_code]) == 1:
                            self.game_codes[game_code].append(conn)
                            self.player_roles[conn] = 2
                            conn.send((json.dumps(
                                {"playerRole": 2, "state": self.game_state, "action": "initial_state"}) + "\n").encode(
                                'utf-8'))

                            # Notify Player 1 that Player 2 has joined
                            player1_conn = self.game_codes[game_code][0]
                            player1_conn.send(
                                (json.dumps({"action": "player2_joined", "state": self.game_state}) + "\n").encode(
                                    'utf-8'))
                        else:
                            conn.send((json.dumps({"error": "Invalid or full game code"}) + "\n").encode('utf-8'))
                    elif data["action"] == "update":
                        game_code = data["code"]
                        if self.player_roles[conn] == self.game_state["playerTurn"]:
                            self.game_state = data["state"]
                            # Ensure Player 2 mirrors Player 1's grid
                            if self.game_state["playerTurn"] == 1:
                                # Broadcast to both players
                                self.broadcast({"state": self.game_state, "action": "sync_grid"}, game_code)  # Switch turn
                            self.broadcast(self.game_state, game_code)
                    elif data["action"] == "disconnect":
                        print(f"{addr} disconnected.")
                        for game_code, conns in self.game_codes.items():
                            if conn in conns:
                                for c in conns:
                                    c.close()
                                del self.game_codes[game_code]
                                break
                        self.player_roles.clear()
                        self.game_state = {"grid": [[None for _ in range(6)] for _ in range(6)], "playerTurn": 1}
                        break

            except (json.JSONDecodeError, socket.error) as e:
                print(f"Error with connection {addr}: {e}")
                break

        conn.close()

    def run_server(self):
        print("Server is running...")
        try:
            while True:
                conn, addr = self.server.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("\nServer shutting down...")
            self.server.close()

if __name__ == "__main__":
    Server().run_server()