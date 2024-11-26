import socket
import threading
import json
import random

class Server:
    def __init__(self, port=5555):
        self.host_ip = socket.gethostbyname(socket.gethostname())
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("", port))
        self.server.listen()
        print("Server started on", self.host_ip, ":", port)

        self.connections = []
        self.game_states = {}
        self.player_roles = {}
        self.lock = threading.Lock()
        self.running = True

    def broadcast(self, data):
        message = json.dumps(data) + "\n"
        for conn in self.connections:
            try:
                conn.send(message.encode('utf-8'))
            except socket.error:
                self.connections.remove(conn)

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
                        self.connections.append(conn)
                        self.player_roles[conn] = 1
                        self.game_states[conn] = {
                            "grid": [[None for _ in range(data.get("cols", 6))] for _ in range(data.get("rows", 6))],
                            "playerTurn": 1,
                            "rows": data.get("rows", 6),
                            "cols": data.get("cols", 6),
                            "expansion": data.get("expansion", 1),
                            "advance_mode": data.get("advance_mode", False)
                        }
                        conn.send((json.dumps({"playerRole": 1}) + "\n").encode('utf-8'))
                    elif data["action"] == "join":
                        if len(self.connections) == 1:
                            self.connections.append(conn)
                            self.player_roles[conn] = 2

                            # Initialize starting positions for both players
                            game_state = self.game_states[self.connections[0]]
                            rows = game_state["rows"]
                            cols = game_state["cols"]

                            # Clear the grid and set initial positions
                            game_state["grid"] = [[None for _ in range(cols)] for _ in range(rows)]
                            # Place Player 1's initial piece on the left side
                            game_state["grid"][random.randint(0, rows - 1)][random.randint(0, cols // 3)] = 1
                            # Place Player 2's initial piece on the right side
                            game_state["grid"][random.randint(0, rows - 1)][random.randint(2 * cols // 3, cols - 1)] = 2

                            game_state["playerTurn"] = 1  # Always start with Player 1

                            self.game_states[self.connections[0]] = game_state

                            # Send initial state to Player 2
                            conn.send((json.dumps({
                                "playerRole": 2,
                                "state": game_state,
                                "action": "initial_state"
                            }) + "\n").encode('utf-8'))

                            # Notify Player 1 that Player 2 has joined
                            player1_conn = self.connections[0]
                            player1_conn.send((json.dumps({
                                "action": "player2_joined",
                                "state": game_state
                            }) + "\n").encode('utf-8'))

                    elif data["action"] == "update":
                        if self.player_roles[conn] == self.game_states[self.connections[0]]["playerTurn"]:
                            # Preserve the game configuration while updating the state
                            current_state = self.game_states[self.connections[0]]
                            new_state = data["state"]
                            current_state["grid"] = new_state["grid"]
                            current_state["playerTurn"] = 2 if current_state["playerTurn"] == 1 else 1
                            self.game_states[self.connections[0]] = current_state
                            self.broadcast(self.game_states[self.connections[0]])

                    elif data["action"] == "disconnect":
                        print(f"{addr} disconnected.")
                        if conn in self.connections:
                            self.connections.remove(conn)
                            conn.close()
                        self.player_roles.clear()
                        break

            except (json.JSONDecodeError, socket.error) as e:
                print(f"Error with connection {addr}: {e}")
                break

        conn.close()

    def run_server(self):
        print("Server is running...")
        try:
            while self.running:
                conn, addr = self.server.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
        except OSError as e:
            print(f"Server stopped: {e}")

    def stop_server(self):
        print("Server is stopping...")
        self.running = False
        self.server.close()
        for conn in self.connections:
            conn.close()
        self.connections.clear()
        self.game_states.clear()
        self.player_roles.clear()

if __name__ == "__main__":
    Server().run_server()