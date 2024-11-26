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
        self.game_states = {}
        self.player_roles = {}
        self.game_codes = {}
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
                        self.game_states[game_code] = {
                            "grid": [[None for _ in range(data.get("cols", 6))] for _ in range(data.get("rows", 6))],
                            "playerTurn": 1,
                            "rows": data.get("rows", 6),
                            "cols": data.get("cols", 6),
                            "expansion": data.get("expansion", 1),
                            "advance_mode": data.get("advance_mode", False)
                        }
                        conn.send((json.dumps({"playerRole": 1, "code": game_code}) + "\n").encode('utf-8'))
                    elif data["action"] == "join":
                        game_code = data["code"]
                        if game_code in self.game_codes and len(self.game_codes[game_code]) == 1:
                            self.game_codes[game_code].append(conn)
                            self.player_roles[conn] = 2

                            # Initialize starting positions for both players
                            game_state = self.game_states[game_code]
                            rows = game_state["rows"]
                            cols = game_state["cols"]

                            # Clear the grid and set initial positions
                            game_state["grid"] = [[None for _ in range(cols)] for _ in range(rows)]
                            # Place Player 1's initial piece on the left side
                            game_state["grid"][random.randint(0, rows - 1)][random.randint(0, cols // 3)] = 1
                            # Place Player 2's initial piece on the right side
                            game_state["grid"][random.randint(0, rows - 1)][random.randint(2 * cols // 3, cols - 1)] = 2

                            game_state["playerTurn"] = 1  # Always start with Player 1

                            self.game_states[game_code] = game_state

                            # Send initial state to Player 2
                            conn.send((json.dumps({
                                "playerRole": 2,
                                "state": game_state,
                                "action": "initial_state"
                            }) + "\n").encode('utf-8'))

                            # Notify Player 1 that Player 2 has joined
                            player1_conn = self.game_codes[game_code][0]
                            player1_conn.send((json.dumps({
                                "action": "player2_joined",
                                "state": game_state
                            }) + "\n").encode('utf-8'))

                    elif data["action"] == "update":
                        game_code = data["code"]
                        if self.player_roles[conn] == self.game_states[game_code]["playerTurn"]:
                            # Preserve the game configuration while updating the state
                            current_state = self.game_states[game_code]
                            new_state = data["state"]
                            current_state["grid"] = new_state["grid"]
                            current_state["playerTurn"] = 2 if current_state["playerTurn"] == 1 else 1
                            self.game_states[game_code] = current_state
                            self.broadcast(self.game_states[game_code], game_code)

                    elif data["action"] == "disconnect":
                        print(f"{addr} disconnected.")
                        for game_code, conns in self.game_codes.items():
                            if conn in conns:
                                for c in conns:
                                    c.close()
                                del self.game_codes[game_code]
                                break
                        self.player_roles.clear()
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