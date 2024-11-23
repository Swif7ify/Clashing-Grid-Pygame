import pygame
import random
import sys

class Game:
    def __init__(self):
        pygame.init()
        self.width, self.height = 750, 750
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.background = (0, 0, 0)
        pygame.display.set_caption("Clashing Grid")
        pygame.display.set_icon(pygame.image.load("objects/iconBLACK.png"))

        self.running = True
        self.playerTurn = 1
        self.player1_score = 0
        self.player2_score = 0

        # canvas screen
        self.canvas_width, self.canvas_height = 600, 538
        self.canvas_screen = pygame.Rect((self.width - 600) // 2, (self.height - 580), self.canvas_width, self.canvas_height)

        # Grid size
        self.rows, self.cols = 5, 5
        self.cell_width = self.canvas_width // self.cols
        self.cell_height = self.canvas_height // self.rows
        self.grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]

        # Colors
        self.player1_color = pygame.image.load("objects/player1Piece.png").convert_alpha()
        self.player1_width, self.player1_height = self.player1_color.get_width(), self.player1_color.get_height()
        self.player1_color = pygame.transform.scale(self.player1_color, (self.cell_width - 15, self.cell_height - 5))

        self.player2_color = pygame.image.load("objects/player2Piece.png").convert_alpha()
        self.player2_width, self.player2_height = self.player2_color.get_width(), self.player2_color.get_height()
        self.player2_color = pygame.transform.scale(self.player2_color, (self.cell_width - 15, self.cell_height - 5))
        self.canvas_color = (29, 30, 30)

        # font
        self.title_font = pygame.font.Font("fonts/Quinquefive-ALoRM.ttf", 18)
        self.sub_title_font = pygame.font.Font("fonts/GamestationCond.otf", 32)

        # delay
        self.delay_active = False
        self.delay_start_time = 0
        self.delay_duration = 2000

        # FPS
        self.clock = pygame.time.Clock()

    def main_menu(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            self.screen.fill(self.background)
            pygame.display.update()

    def draw_grid(self):
        for row in range(self.rows):
            for col in range(self.cols):
                x = self.canvas_screen.x + col * self.cell_width
                y = self.canvas_screen.y + row * self.cell_height

                pygame.draw.rect(self.screen, 0, (x, y, self.cell_width, self.cell_height))
                pygame.draw.rect(self.screen, (75, 75, 75), (x, y, self.cell_width, self.cell_height), 1)

                if self.grid[row][col] == 1:
                    self.screen.blit(self.player1_color, (x + 7, y + 2))
                elif self.grid[row][col] == 2:
                    self.screen.blit(self.player2_color, (x + 7, y + 2))

    def place_initial_cell(self):
        self.player1_score = 0
        self.player2_score = 0
        self.grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.playerTurn = 1

        self.grid[random.randint(1, self.rows) // 2][self.cols // 3] = 1
        self.grid[random.randint(1, self.rows) // 2][2 * self.cols // 3] = 2

    def get_neighbors(self, row, col):
        neighbors = []
        for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                neighbors.append((nr, nc))
        return neighbors

    def random_expand(self, row, col):
        neighbors = self.get_neighbors(row, col)
        valid_neighbors = [(nr, nc) for nr, nc in neighbors if self.grid[nr][nc] is None]

        if valid_neighbors:
            new_cell = random.choice(valid_neighbors)
            self.grid[new_cell[0]][new_cell[1]] = self.playerTurn

    def handle_click(self, pos):
        x, y = pos
        col = (x - self.canvas_screen.x) // self.cell_width
        row = (y - self.canvas_screen.y) // self.cell_height

        if 0 <= row < self.rows and 0 <= col < self.cols:  # Ensure click is within the grid
            if self.grid[row][col] is None:  # If the clicked cell is empty
                neighbors = self.get_neighbors(row, col)
                if any(self.grid[nr][nc] == self.playerTurn for nr, nc in neighbors):  # Valid neighbor check
                    self.grid[row][col] = self.playerTurn  # Update the grid
                    self.random_expand(row, col)  # Expand to a random valid neighbor
                    self.playerTurn = 2 if self.playerTurn == 1 else 1  # Alternate turn

    def check_winner(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] is None:
                    neighbors = self.get_neighbors(row, col)
                    if any(self.grid[nr][nc] == self.playerTurn for nr, nc in neighbors):
                        return  # Current player has valid moves, continue the game

        # If no valid moves, fill all remaining cells with the opponent's pieces
        opponent = 2 if self.playerTurn == 1 else 1
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] is None:
                    self.grid[row][col] = opponent

        # Proceed to the winner method
        pygame.display.update()
        self.delay_active = True
        self.delay_start_time = pygame.time.get_ticks()


    def winner(self):
        if self.player1_score == self.player2_score:
            game_overText = self.title_font.render("Draw", True, (255, 255, 255))
            game_overText_rect = game_overText.get_rect(center=(self.width // 2, 100))
            playerImg = pygame.transform.scale(pygame.image.load("objects/drawnGame.png").convert_alpha(), (300, 300))
            playerImg_rect = playerImg.get_rect(center=(self.width // 2, self.height // 2 - 30))
        else:
            game_overText = self.title_font.render(f"Player {1 if self.player1_score > self.player2_score else 2} WINS! ", True, (255, 255, 255))
            game_overText_rect = game_overText.get_rect(center=(self.width // 2, 100))
            playerImg = pygame.transform.scale(pygame.image.load(
                "objects/player1Crowned.png" if self.player1_score > self.player2_score else "objects/player2Crowned.png").convert_alpha(),
                                               (300, 300))
            playerImg_rect = playerImg.get_rect(center=(self.width // 2, self.height // 2 - 30))

        try_againText = self.title_font.render("Try Again?", True, (255, 255, 255))
        try_againText_rect = try_againText.get_rect(center=(self.width // 2, 140))

        main_menuText = self.sub_title_font.render("Main Menu", True, (255, 255, 255))
        main_menuText_rect = main_menuText.get_rect(center=(self.width // 2, self.height // 2 + 180))

        restartText = self.sub_title_font.render("Restart", True, (255, 255, 255))
        restartText_rect = restartText.get_rect(center=(self.width // 2, self.height // 2 + 230))

        quitText = self.sub_title_font.render("Quit", True, (255, 255, 255))
        quitText_rect = quitText.get_rect(center=(self.width // 2, self.height // 2 + 280))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    if main_menuText_rect.collidepoint(event.pos) or restartText_rect.collidepoint(event.pos) or quitText_rect.collidepoint(event.pos):
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    else:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if restartText_rect.collidepoint(event.pos):
                        self.place_initial_cell()
                        return
                    elif main_menuText_rect.collidepoint(event.pos):
                        self.run()
                        return
                    elif quitText_rect.collidepoint(event.pos):
                        sys.exit()

            self.screen.fill(self.background)
            self.screen.blit(game_overText, game_overText_rect)
            self.screen.blit(try_againText, try_againText_rect)
            self.screen.blit(playerImg, playerImg_rect)
            self.screen.blit(main_menuText, main_menuText_rect)
            self.screen.blit(restartText, restartText_rect)
            self.screen.blit(quitText, quitText_rect)
            pygame.display.update()

    def player_score(self):
        self.player1_score = sum(cell == 1 for row in self.grid for cell in row)
        self.player2_score = sum(cell == 2 for row in self.grid for cell in row)

    def draw_header(self):
        title_text = self.title_font.render(f"Player {self.playerTurn}", True, (255, 255, 255))
        title_text_rect = title_text.get_rect(center=(self.width // 2, 100))

        player1_score = self.title_font.render(f"P1:{self.player1_score}", True, (255, 255, 255))
        player2_score = self.title_font.render(f"P2:{self.player2_score}", True, (255, 255, 255))

        self.screen.blit(title_text, title_text_rect)
        self.screen.blit(player1_score, (self.width // 10, 130))
        self.screen.blit(player2_score, (590, 130))

    def run(self):
        # self.main_menu()
        self.place_initial_cell()

        pauseButton = pygame.transform.scale(pygame.image.load("objects/pauseButton.png").convert_alpha(), (40, 40))
        pauseButton_rect = pauseButton.get_rect(center=(self.width - 50, 40))
        while self.running:
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.MOUSEMOTION:
                    if pauseButton_rect.collidepoint(event.pos):
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    else:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pauseButton_rect.collidepoint(event.pos):
                        print("Pause Button Clicked")
                    elif self.canvas_screen.collidepoint(event.pos):
                        self.handle_click(event.pos)

            self.screen.fill(self.background)
            self.screen.blit(pauseButton, pauseButton_rect)
            self.player_score()
            self.draw_header() # draws game header
            self.draw_grid() # draws grid
            if self.delay_active:
                current_time = pygame.time.get_ticks()
                if current_time - self.delay_start_time >= self.delay_duration:
                    self.delay_active = False
                    self.winner()
            else:
                self.check_winner()
            self.clock.tick(60)
            pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()
    sys.exit()

# implementation of main screen